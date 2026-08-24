CREATE TABLE IF NOT EXISTS articles (
    page_id BIGINT PRIMARY KEY,
    title TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS crawl_runs (
    run_id BIGSERIAL PRIMARY KEY,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    requested_limit INTEGER,
    article_count INTEGER NOT NULL,
    link_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS run_articles (
    run_id BIGINT NOT NULL REFERENCES crawl_runs(run_id) ON DELETE CASCADE,
    page_id BIGINT NOT NULL REFERENCES articles(page_id),
    assessment_class TEXT,
    importance TEXT,
    community_id INTEGER,
    PRIMARY KEY (run_id, page_id)
);

CREATE TABLE IF NOT EXISTS run_article_links (
    run_id BIGINT NOT NULL,
    source_id BIGINT NOT NULL,
    destination_id BIGINT NOT NULL,
    PRIMARY KEY (run_id, source_id, destination_id),
    FOREIGN KEY (run_id, source_id)
        REFERENCES run_articles(run_id, page_id) ON DELETE CASCADE,
    FOREIGN KEY (run_id, destination_id)
        REFERENCES run_articles(run_id, page_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS run_article_links_destination_idx
    ON run_article_links (run_id, destination_id);

CREATE INDEX IF NOT EXISTS run_articles_community_idx
    ON run_articles (run_id, community_id);
