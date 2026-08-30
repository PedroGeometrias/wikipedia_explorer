const colors = [
  "#e41a1c",
  "#377eb8",
  "#4daf4a",
  "#984ea3",
  "#ff7f00",
  "#ffff33",
  "#a65628",
  "#f781bf",
];

const info = document.getElementById("info");
const bfsButton = document.getElementById("bfs-button");
const searchInput = document.getElementById("search");
const reset_btn = document.getElementById("reset-all");
const backButton = document.getElementById("back-button");
const forwardButton = document.getElementById("forward-button");

let graphView;
let graphData;
let module;
let graphPointer;
let historyPointer;
let selectedNode = null;
let bfsDistances = null;
let previousView = null;

function nodeColor(node) {
  if (selectedNode && node.id === selectedNode.id) {
    return "#ffffff";
  }
  if (bfsDistances) {
    const distance = bfsDistances[node.id];
    if (distance === 0xffffffff) return "#333333";
    return `hsl(${Math.max(20, 200 - distance * 25)}, 80%, 55%)`;
  }
  return colors[node.community % colors.length];
}

function showNode(node) {
  selectedNode = node;
  bfsButton.disabled = false;
  info.replaceChildren();
  const title = document.createElement("strong");
  title.textContent = node.title;
  const wiki_link = document.createElement("a");
  wiki_link.href = `https://en.wikipedia.org/wiki/${encodeURIComponent(
    node.title.replaceAll(" ", "_"),
  )}`;
  wiki_link.target = "_blank";
  wiki_link.rel = "noopener noreferrer";
  wiki_link.textContent = "Open on Wikipedia ";
  info.append(
    title,
    document.createElement("br"),
    `In-degree: ${node.inDegree}`,
    document.createElement("br"),
    `Out-degree: ${node.outDegree}`,
    document.createElement("br"),
    `PageRank: ${node.pageRank.toFixed(6)}`,
    document.createElement("br"),
    wiki_link,
  );
  graphView.nodeColor(nodeColor);
}

function focusNode(node, recordHistory = true) {
  if (recordHistory) {
    module._history_visit(historyPointer, node.id);
    updateHistoryButtons();
  }
  if (!previousView) {
    const position = graphView.cameraPosition();
    const target = graphView.controls().target;

    previousView = {
      position: {
        x: position.x,
        y: position.y,
        z: position.z,
      },
      target: {
        x: target.x,
        y: target.y,
        z: target.z,
      },
    };
  }

  const distance = Math.hypot(node.x, node.y, node.z) || 1;
  const ratio = 1 + 50 / distance;

  graphView.cameraPosition(
    { x: node.x * ratio, y: node.y * ratio, z: node.z * ratio },
    node,
    800,
  );

  showNode(node);
}

function copyGraphToWasm() {
  const sources = Uint32Array.from(graphData.links, (link) => link.source);
  const destinations = Uint32Array.from(graphData.links, (link) => link.target);
  const sourcePointer = module._malloc(sources.byteLength);
  const destinationPointer = module._malloc(destinations.byteLength);

  module.HEAPU32.set(sources, sourcePointer / 4);
  module.HEAPU32.set(destinations, destinationPointer / 4);
  graphPointer = module._graph_create(
    graphData.nodes.length,
    graphData.links.length,
  );
  module._graph_set_edges(graphPointer, sourcePointer, destinationPointer);

  module._free(sourcePointer);
  module._free(destinationPointer);
}

function calculateMetrics() {
  const count = graphData.nodes.length;
  const outPointer = module._malloc(count * 4);
  const inPointer = module._malloc(count * 4);
  const rankPointer = module._malloc(count * 8);

  module._compute_degrees(graphPointer, outPointer, inPointer);
  module._pagerank(graphPointer, 0.85, 1e-8, 100, rankPointer);

  const outDegrees = module.HEAPU32.slice(
    outPointer / 4,
    outPointer / 4 + count,
  );
  const inDegrees = module.HEAPU32.slice(inPointer / 4, inPointer / 4 + count);
  const pageRanks = module.HEAPF64.slice(
    rankPointer / 8,
    rankPointer / 8 + count,
  );

  graphData.nodes.forEach((node, index) => {
    node.outDegree = outDegrees[index];
    node.inDegree = inDegrees[index];
    node.pageRank = pageRanks[index];
  });

  module._free(outPointer);
  module._free(inPointer);
  module._free(rankPointer);
}
function updateHistoryButtons() {
  backButton.disabled = !module._history_can_back(historyPointer);

  forwardButton.disabled = !module._history_can_forward(historyPointer);
}

async function start() {
  if (typeof createGraphModule !== "function") {
    throw new Error("WebAssembly is missing. Run: make wasm");
  }

  graphData = await fetch("graph.json").then((response) => response.json());
  module = await createGraphModule();
  historyPointer = module._history_create();

  if (!historyPointer) {
    throw new Error("Could not create navigation history.");
  }
  copyGraphToWasm();
  calculateMetrics();

  graphView = ForceGraph3D()(document.getElementById("graph"))
    .graphData(graphData)
    .backgroundColor("#000000")
    .nodeLabel("title")
    .nodeColor(nodeColor)
    .nodeVal((node) => 2 + node.pageRank * graphData.nodes.length * 4)
    .linkColor(() => "#555555")
    .linkOpacity(0.35)
    .linkDirectionalArrowLength(2)
    .onNodeClick(focusNode)
    .enableNodeDrag(false);

  const controls = graphView.controls();
  controls.rotateSpeed = 0.5;
  controls.zoomSpeed = 0.3;
  controls.panSpeed = 0.1;
}

bfsButton.addEventListener("click", () => {
  if (!selectedNode) return;
  const count = graphData.nodes.length;
  const distancePointer = module._malloc(count * 4);
  module._bfs(graphPointer, selectedNode.id, distancePointer);
  bfsDistances = module.HEAPU32.slice(
    distancePointer / 4,
    distancePointer / 4 + count,
  );
  module._free(distancePointer);
  graphView.nodeColor(nodeColor);
});

backButton.addEventListener("click", () => {
  const nodeId = module._history_back(historyPointer);

  if (nodeId === 0xffffffff) {
    return;
  }

  const node = graphData.nodes[nodeId];

  focusNode(node, false);
  updateHistoryButtons();
});

const randomButton = document.getElementById("random-button");

randomButton.addEventListener("click", () => {
  const node =
    graphData.nodes[Math.floor(Math.random() * graphData.nodes.length)];

  focusNode(node);
});

forwardButton.addEventListener("click", () => {
  const nodeId = module._history_forward(historyPointer);

  if (nodeId === 0xffffffff) {
    return;
  }

  const node = graphData.nodes[nodeId];

  focusNode(node, false);
  updateHistoryButtons();
});

reset_btn.addEventListener("click", () => {
  selectedNode = null;
  bfsDistances = null;

  searchInput.value = "";
  bfsButton.disabled = true;

  module._history_clear(historyPointer);
  updateHistoryButtons();

  info.textContent = "CLICK NODE TO INSPECT IT";
  graphView.nodeColor(nodeColor);

  if (previousView) {
    graphView.cameraPosition(previousView.position, previousView.target, 800);

    previousView = null;
  }
});
document.getElementById("search-button").addEventListener("click", () => {
  const query = searchInput.value.trim().toLowerCase();
  if (!query) return;
  const node = graphData.nodes.find((item) =>
    item.title.toLowerCase().includes(query),
  );
  if (node) focusNode(node);
});

window.addEventListener("beforeunload", () => {
  if (module && historyPointer) {
    module._history_destroy(historyPointer);
  }

  if (module && graphPointer) {
    module._graph_free(graphPointer);
  }
});
start().catch((error) => {
  info.textContent = error.message;
  console.error(error);
});
