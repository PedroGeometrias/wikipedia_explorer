from graph_loader import load_graph_from_db
from community_detection import detect_communities
from visualization import visualize_2d


def main():
    # 1. Load graph from PostgreSQL (source of truth)
    G = load_graph_from_db()
    print(f"Loaded graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

    # 2. Detect communities (clusters)
    communities = detect_communities(G, method="louvain")
    print(f"Detected {len(communities)} communities.")

    # 3. Visualize in 2D
    visualize_2d(G, communities, save_path="wikipedia_graph.png", show=True)


if __name__ == "__main__":
    main()
