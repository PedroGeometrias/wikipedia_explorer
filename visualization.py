import matplotlib.pyplot as plt
import networkx as nx
from community_detection import detect_communities


def _community_color_map(G, communities):
    """
    Map each node to an integer community ID.
    """
    node_to_community = {}
    for idx, community in enumerate(communities):
        for node in community:
            node_to_community[node] = idx
    return node_to_community


def visualize_2d(G, communities=None, save_path=None, show=True):
    """
    Draw the graph in 2D, coloured by community.

    Args:
        G (nx.DiGraph): Directed graph.
        communities (list of sets, optional): Pre‑computed communities.
                                              If None, they will be detected.
        save_path (str, optional): If provided, the figure is saved to this path.
        show (bool): If True, display the plot interactively.
    """
    if communities is None:
        communities = detect_communities(G)

    node_to_community = _community_color_map(G, communities)

    # Use a colormap with enough distinct colours
    cmap = plt.get_cmap("tab20")
    node_colors = [cmap(node_to_community.get(node, 0) % 20) for node in G.nodes()]

    # Scale node size by total degree (in+out), min size 150
    node_sizes = [150 + 50 * G.degree(node) for node in G.nodes()]

    # Spring layout often reveals clusters nicely
    pos = nx.spring_layout(G, seed=42, k=0.5, iterations=50)

    # Draw nodes, edges, labels
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)
    nx.draw_networkx_edges(G, pos, edge_color="gray", alpha=0.3, arrows=True,
                           arrowstyle='-|>', arrowsize=8)

    # Draw labels (titles)
    labels = {node: G.nodes[node].get("title", str(node)) for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=6)

    plt.title(f"Wikipedia Mathematics Link Graph\n{len(communities)} communities detected")
    plt.axis("off")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved figure to {save_path}")

    if show:
        plt.show()

    plt.close()
