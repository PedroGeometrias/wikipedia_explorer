# Fetch a set of WikiProject Mathematics articles and build directed edges
# between articles that link to one another inside that selected set.

import requests

URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "WikipediaExplorer/0.1"}


def fetch_wikipedia_articles(limit: int = 50):
    """
    Fetch articles from WikiProject Mathematics and the links between them.

    Args:
        limit (int): Number of WikiProject Mathematics articles to fetch.
                     The current single-request implementation is intended
                     for up to 50 articles.

    Returns:
        tuple: (articles, edges)
            articles: list of Wikipedia article dictionaries, including
                      page ID, title, and assessment data when available.
            edges: list of (source_page_id, destination_page_id) tuples.
    """
    # --------------------------------------------------
    # 1. Get a number of Wikipedia articles
    # --------------------------------------------------
    params = {
        "action": "query",
        "format": "json",
        "list": "projectpages",
        "wppprojects": "Mathematics",
        "wppassessments": "true",
        "wpplimit": limit,
    }

    res = requests.get(URL, params=params, headers=HEADERS, timeout=10)
    res.raise_for_status()
    data = res.json()

    articles = data.get("query", {}).get("projects", {}).get("Mathematics", [])

    if not articles:
        print("No articles found.")
        return [], []

    # --------------------------------------------------
    # 2. Build a helper lookup: title -> page ID
    # --------------------------------------------------
    selected_articles = {}

    for article in articles:
        title = article["title"]
        page_id = article["pageid"]
        selected_articles[title] = page_id

    print("SELECTED ARTICLES:")

    for title, page_id in selected_articles.items():
        print(page_id, title)

    # --------------------------------------------------
    # 3. Prepare selected titles and IDs for the API
    # --------------------------------------------------
    selected_titles = "|".join(selected_articles.keys())
    page_ids = "|".join(str(page_id) for page_id in selected_articles.values())

    # --------------------------------------------------
    # 4. Fetch links for all selected articles at once,
    #    restricted to destinations inside our dataset
    # --------------------------------------------------
    link_params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "prop": "links",
        "pageids": page_ids,
        "plnamespace": "0",
        "pltitles": selected_titles,
        "pllimit": "max",
    }

    res = requests.get(URL, params=link_params, headers=HEADERS, timeout=10)
    res.raise_for_status()
    link_data = res.json()

    # --------------------------------------------------
    # 5. Build directed graph edges
    # --------------------------------------------------
    edges = []

    for page in link_data.get("query", {}).get("pages", []):
        source_id = page.get("pageid")

        if source_id is None:
            continue

        for link in page.get("links", []):
            destination_title = link.get("title")

            if destination_title in selected_articles:
                destination_id = selected_articles[destination_title]
                edges.append((source_id, destination_id))

    print("\nEDGES:")

    for source_id, destination_id in edges:
        print(source_id, "->", destination_id)

    # Return the full article records for PostgreSQL, not the helper lookup.
    return articles, edges
