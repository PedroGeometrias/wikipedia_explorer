import networkx as nx

from save_wiki_db import connect, resolve_run_id


def load_graph_from_db(run_id=None):
    """Load the latest crawl snapshot, or a specific run, from PostgreSQL."""
    with connect() as conn:
        resolved_run_id = resolve_run_id(conn, run_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    a.page_id,
                    a.title,
                    ra.assessment_class,
                    ra.importance,
                    ra.community_id
                FROM run_articles ra
                JOIN articles a ON a.page_id = ra.page_id
                WHERE ra.run_id = %s
                """,
                (resolved_run_id,),
            )
            articles = cur.fetchall()

            cur.execute(
                """
                SELECT source_id, destination_id
                FROM run_article_links
                WHERE run_id = %s
                """,
                (resolved_run_id,),
            )
            edges = cur.fetchall()

    graph = nx.DiGraph(run_id=resolved_run_id)
    for page_id, title, assessment_class, importance, community_id in articles:
        graph.add_node(
            page_id,
            title=title,
            assessment_class=assessment_class,
            importance=importance,
            community_id=community_id,
        )
    graph.add_edges_from(edges)
    return graph
