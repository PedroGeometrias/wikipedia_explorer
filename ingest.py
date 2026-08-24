import argparse

from fetch_wikipedia import fetch_wikipedia_articles
from save_wiki_db import save_graph


def ingest(limit=50):
    articles, edges = fetch_wikipedia_articles(limit)
    run_id = save_graph(articles, edges, requested_limit=limit)
    print(f"Saved crawl run {run_id}")
    return run_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()
    ingest(args.limit)
