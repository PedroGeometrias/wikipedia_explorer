import argparse
import json
from pathlib import Path

from community_detection import detect_communities
from graph_loader import load_graph_from_db
from save_wiki_db import save_communities


def export_graph(output_path="docs/graph.json", run_id=None):
    """Export the latest snapshot, or a selected run, as frontend JSON."""
    graph = load_graph_from_db(run_id)
    resolved_run_id = graph.graph["run_id"]
    communities = detect_communities(graph)
    save_communities(resolved_run_id, communities)

    page_ids = sorted(graph.nodes())
    node_ids = {page_id: index for index, page_id in enumerate(page_ids)}
    community_ids = {
        page_id: community_id
        for community_id, community in enumerate(communities)
        for page_id in community
    }

    data = {
        "run_id": resolved_run_id,
        "nodes": [
            {
                "id": node_ids[page_id],
                "page_id": page_id,
                "title": graph.nodes[page_id].get("title", str(page_id)),
                "community": community_ids.get(page_id, 0),
            }
            for page_id in page_ids
        ],
        "links": [
            {"source": node_ids[source], "target": node_ids[target]}
            for source, target in graph.edges()
        ],
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(
        f"Exported run {resolved_run_id}: {len(data['nodes'])} nodes and "
        f"{len(data['links'])} links to {output}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", type=int, help="crawl run to export; defaults to latest")
    parser.add_argument("--output", default="docs/graph.json")
    args = parser.parse_args()
    export_graph(args.output, args.run_id)
