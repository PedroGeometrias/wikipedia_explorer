import networkx as nx
# boring, I used the lib instead of writing this in c because of time, will try writing this myself though[GREP_THIS_LATER]

def detect_communities(G, method="louvain"):
    """
    Detect communities in the undirected version of the graph.

    Args:
        G (nx.DiGraph): Directed graph.
        method (str): "louvain" or "greedy".

    Returns:
        list of sets: Each set contains the nodes belonging to one community.
    """
    undirected = G.to_undirected()

    if method == "louvain":
        try:
            # NetworkX >= 2.6 has built-in Louvain
            return list(nx.algorithms.community.louvain_communities(undirected, seed=42))
        except AttributeError:
            print("Louvain not available, falling back to greedy modularity.")
            return list(nx.algorithms.community.greedy_modularity_communities(undirected))

    elif method == "greedy":
        return list(nx.algorithms.community.greedy_modularity_communities(undirected))

    else:
        raise ValueError(f"Unknown method: {method}")
