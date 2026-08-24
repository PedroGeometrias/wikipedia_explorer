import time
from itertools import islice

import requests


URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": (
        "WikipediaExplorer/0.1 "
        "(https://github.com/PedroGeometrias/wikipedia_explorer)"
    )
}

BATCH_SIZE = 50
REQUEST_DELAY = 0.25
MAX_RETRIES = 6
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def chunks(iterable, size):
    """Yield successive chunks from an iterable."""
    iterator = iter(iterable)

    while True:
        chunk = list(islice(iterator, size))

        if not chunk:
            return

        yield chunk


def get_json(session, params):
    """Send a Wikipedia API request with basic retry handling."""
    for attempt in range(MAX_RETRIES):
        response = session.get(
            URL,
            params=params,
            headers=HEADERS,
            timeout=30,
        )

        if response.status_code in RETRYABLE_STATUS_CODES:
            retry_after = response.headers.get("Retry-After", "")
            wait = (
                int(retry_after)
                if retry_after.isdigit()
                else 2 ** attempt
            )

            response.close()
            time.sleep(wait)
            continue

        response.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return response.json()

    raise RuntimeError(
        "Wikipedia API request failed after repeated retries"
    )


def fetch_wikipedia_articles(limit: int = 50):
    """
    Fetch WikiProject Mathematics articles and the links between them.

    Article discovery uses Wikipedia continuation tokens. Link requests
    are divided into batches to stay within the API parameter limits.

    Args:
        limit: Maximum number of articles to fetch.

    Returns:
        A tuple containing the article records and graph edges.
    """
    if limit < 1:
        raise ValueError("limit must be at least 1")

    articles = []

    project_params = {
        "action": "query",
        "format": "json",
        "list": "projectpages",
        "wppprojects": "Mathematics",
        "wppassessments": "true",
    }

    with requests.Session() as session:
        # ----------------------------------------------
        # 1. Fetch articles using API continuation
        # ----------------------------------------------
        while len(articles) < limit:
            project_params["wpplimit"] = min(
                BATCH_SIZE,
                limit - len(articles),
            )

            data = get_json(session, project_params)

            batch = (
                data.get("query", {})
                .get("projects", {})
                .get("Mathematics", [])
            )

            if not batch:
                break

            articles.extend(batch)

            if len(articles) >= limit:
                break

            if "continue" not in data:
                break

            project_params.update(data["continue"])

        if not articles:
            print("No articles found.")
            return [], []

        selected_articles = {
            article["title"]: article["pageid"]
            for article in articles
        }

        page_ids = [
            article["pageid"]
            for article in articles
        ]

        selected_titles = list(selected_articles)
        edges = set()

        # ----------------------------------------------
        # 2. Fetch links using source/destination batches
        # ----------------------------------------------
        for id_batch in chunks(page_ids, BATCH_SIZE):
            for title_batch in chunks(
                selected_titles,
                BATCH_SIZE,
            ):
                link_params = {
                    "action": "query",
                    "format": "json",
                    "formatversion": "2",
                    "prop": "links",
                    "pageids": "|".join(
                        str(page_id)
                        for page_id in id_batch
                    ),
                    "pltitles": "|".join(title_batch),
                    "plnamespace": "0",
                    "pllimit": "max",
                }

                while True:
                    link_data = get_json(
                        session,
                        link_params,
                    )

                    pages = (
                        link_data
                        .get("query", {})
                        .get("pages", [])
                    )

                    for page in pages:
                        source_id = page.get("pageid")

                        if source_id is None:
                            continue

                        for link in page.get("links", []):
                            destination_id = (
                                selected_articles.get(
                                    link.get("title")
                                )
                            )

                            if destination_id is not None:
                                edges.add(
                                    (
                                        source_id,
                                        destination_id,
                                    )
                                )

                    if "continue" not in link_data:
                        break

                    link_params.update(
                        link_data["continue"]
                    )

    print(f"Selected {len(articles)} articles.")
    print(
        f"Found {len(edges)} links "
        "between selected articles."
    )

    return articles, sorted(edges)
