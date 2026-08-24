import argparse

import psycopg

from fetch_wikipedia import fetch_wikipedia_articles
from save_wiki_db import (
    connect,
    initialize_schema,
    save_graph,
)


def check_database():
    """Verify the database before making Wikipedia API requests."""
    try:
        with connect() as conn:
            initialize_schema(conn)
    except psycopg.Error as error:
        raise SystemExit(
            f"Database connection failed: {error}"
        ) from None

    print("Database connection: OK")


def ingest(limit=50):
    check_database()

    articles, edges = fetch_wikipedia_articles(limit)

    run_id = save_graph(
        articles,
        edges,
        requested_limit=limit,
    )

    print(f"Saved crawl run {run_id}")
    return run_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
    )
    args = parser.parse_args()

    ingest(args.limit)
