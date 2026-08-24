"""PostgreSQL connection and versioned graph persistence."""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

load_dotenv()


def connect():
    return psycopg.connect(
        dbname=os.getenv("PG_DB"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST", "localhost"),
    )


def initialize_schema(conn):
    schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    with conn.cursor() as cur:
        for statement in schema.split(";"):
            if statement.strip():
                cur.execute(statement)


def resolve_run_id(conn, run_id=None):
    if run_id is not None:
        with conn.cursor() as cur:
            cur.execute("SELECT run_id FROM crawl_runs WHERE run_id = %s", (run_id,))
            if cur.fetchone() is None:
                raise ValueError(f"crawl run {run_id} does not exist")
        return run_id

    with conn.cursor() as cur:
        cur.execute("SELECT MAX(run_id) FROM crawl_runs")
        latest = cur.fetchone()[0]

    if latest is None:
        raise ValueError("no crawl runs have been saved")
    return latest


def save_articles(conn, run_id, articles):
    article_rows = []
    run_rows = []

    for article in articles:
        assessment = article.get("assessment", {})
        article_rows.append((article["pageid"], article["title"]))
        run_rows.append(
            (
                run_id,
                article["pageid"],
                assessment.get("class"),
                assessment.get("importance"),
            )
        )

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO articles (page_id, title)
            VALUES (%s, %s)
            ON CONFLICT (page_id) DO UPDATE SET title = EXCLUDED.title
            """,
            article_rows,
        )
        cur.executemany(
            """
            INSERT INTO run_articles (
                run_id, page_id, assessment_class, importance
            )
            VALUES (%s, %s, %s, %s)
            """,
            run_rows,
        )


def save_edges(conn, run_id, edges):
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO run_article_links (run_id, source_id, destination_id)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            [(run_id, source_id, destination_id) for source_id, destination_id in edges],
        )


def save_graph(articles, edges, requested_limit=None):
    """Save one immutable crawl snapshot and return its run ID."""
    if requested_limit is None:
        requested_limit = len(articles)

    with connect() as conn:
        initialize_schema(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO crawl_runs (
                    requested_limit, article_count, link_count
                )
                VALUES (%s, %s, %s)
                RETURNING run_id
                """,
                (requested_limit, len(articles), len(edges)),
            )
            run_id = cur.fetchone()[0]

        save_articles(conn, run_id, articles)
        save_edges(conn, run_id, edges)

    return run_id


def save_communities(run_id, communities):
    """Replace the stored community assignments for one crawl snapshot."""
    assignments = [
        (community_id, run_id, page_id)
        for community_id, community in enumerate(communities)
        for page_id in community
    ]

    with connect() as conn:
        resolved_run_id = resolve_run_id(conn, run_id)
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE run_articles SET community_id = NULL WHERE run_id = %s",
                (resolved_run_id,),
            )
            cur.executemany(
                """
                UPDATE run_articles
                SET community_id = %s
                WHERE run_id = %s AND page_id = %s
                """,
                assignments,
            )
