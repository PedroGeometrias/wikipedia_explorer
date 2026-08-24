"""Small SQL helpers for inspecting and comparing crawl snapshots."""

from save_wiki_db import connect, resolve_run_id


def list_runs():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT run_id, fetched_at, requested_limit, article_count, link_count
                FROM crawl_runs
                ORDER BY run_id DESC
                """
            )
            return cur.fetchall()


def get_out_degrees(run_id=None):
    with connect() as conn:
        resolved_run_id = resolve_run_id(conn, run_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT a.page_id, a.title, COUNT(l.destination_id) AS out_degree
                FROM run_articles ra
                JOIN articles a ON a.page_id = ra.page_id
                LEFT JOIN run_article_links l
                    ON l.run_id = ra.run_id AND l.source_id = ra.page_id
                WHERE ra.run_id = %s
                GROUP BY a.page_id, a.title
                ORDER BY out_degree DESC, a.title
                """,
                (resolved_run_id,),
            )
            return cur.fetchall()


def get_in_degrees(run_id=None):
    with connect() as conn:
        resolved_run_id = resolve_run_id(conn, run_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT a.page_id, a.title, COUNT(l.source_id) AS in_degree
                FROM run_articles ra
                JOIN articles a ON a.page_id = ra.page_id
                LEFT JOIN run_article_links l
                    ON l.run_id = ra.run_id AND l.destination_id = ra.page_id
                WHERE ra.run_id = %s
                GROUP BY a.page_id, a.title
                ORDER BY in_degree DESC, a.title
                """,
                (resolved_run_id,),
            )
            return cur.fetchall()


def get_community_sizes(run_id=None):
    with connect() as conn:
        resolved_run_id = resolve_run_id(conn, run_id)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT community_id, COUNT(*) AS article_count
                FROM run_articles
                WHERE run_id = %s AND community_id IS NOT NULL
                GROUP BY community_id
                ORDER BY article_count DESC, community_id
                """,
                (resolved_run_id,),
            )
            return cur.fetchall()


def compare_runs(old_run_id, new_run_id):
    """Return article/link counts added and removed between two snapshots."""
    with connect() as conn:
        old_run_id = resolve_run_id(conn, old_run_id)
        new_run_id = resolve_run_id(conn, new_run_id)
        with conn.cursor() as cur:
            return {
                "old_run_id": old_run_id,
                "new_run_id": new_run_id,
                "articles_added": _difference_count(
                    cur, "run_articles", "page_id", new_run_id, old_run_id
                ),
                "articles_removed": _difference_count(
                    cur, "run_articles", "page_id", old_run_id, new_run_id
                ),
                "links_added": _difference_count(
                    cur,
                    "run_article_links",
                    "source_id, destination_id",
                    new_run_id,
                    old_run_id,
                ),
                "links_removed": _difference_count(
                    cur,
                    "run_article_links",
                    "source_id, destination_id",
                    old_run_id,
                    new_run_id,
                ),
            }


def _difference_count(cur, table, columns, left_run_id, right_run_id):
    allowed = {
        ("run_articles", "page_id"),
        ("run_article_links", "source_id, destination_id"),
    }
    if (table, columns) not in allowed:
        raise ValueError("unsupported snapshot comparison")

    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM (
            SELECT {columns} FROM {table} WHERE run_id = %s
            EXCEPT
            SELECT {columns} FROM {table} WHERE run_id = %s
        ) AS difference
        """,
        (left_run_id, right_run_id),
    )
    return cur.fetchone()[0]
