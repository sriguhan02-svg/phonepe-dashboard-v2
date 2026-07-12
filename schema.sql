-- PhonePe Pulse SQLite Schema
-- Tables are created automatically by extract_pipeline.py (pandas to_sql),
-- this file documents the structure for the repo / README and lets anyone
-- inspect the design without running the pipeline.

CREATE TABLE IF NOT EXISTS agg_transaction (
    state TEXT, year INTEGER, quarter TEXT,
    transaction_type TEXT, count INTEGER, amount REAL
);

CREATE TABLE IF NOT EXISTS agg_user (
    state TEXT, year INTEGER, quarter TEXT,
    brand TEXT, count INTEGER, percentage REAL
);

CREATE TABLE IF NOT EXISTS agg_insurance (
    state TEXT, year INTEGER, quarter TEXT,
    transaction_type TEXT, count INTEGER, amount REAL
);

CREATE TABLE IF NOT EXISTS map_transaction (
    state TEXT, year INTEGER, quarter TEXT,
    district TEXT, metric_type TEXT, count INTEGER, amount REAL
);

CREATE TABLE IF NOT EXISTS map_user (
    state TEXT, year INTEGER, quarter TEXT,
    district TEXT, registered_users INTEGER, app_opens INTEGER
);

CREATE TABLE IF NOT EXISTS map_insurance (
    state TEXT, year INTEGER, quarter TEXT,
    district TEXT, metric_type TEXT, count INTEGER, amount REAL
);

CREATE TABLE IF NOT EXISTS top_transaction (
    state TEXT, year INTEGER, quarter TEXT,
    level TEXT, entity TEXT, metric_type TEXT, count INTEGER, amount REAL
);

CREATE TABLE IF NOT EXISTS top_user (
    state TEXT, year INTEGER, quarter TEXT,
    level TEXT, entity TEXT, registered_users INTEGER
);

CREATE TABLE IF NOT EXISTS top_insurance (
    state TEXT, year INTEGER, quarter TEXT,
    level TEXT, entity TEXT, metric_type TEXT, count INTEGER, amount REAL
);

-- Recommended indices for the columns you'll filter/group by most in Power BI
CREATE INDEX IF NOT EXISTS idx_agg_tx_state_year ON agg_transaction(state, year);
CREATE INDEX IF NOT EXISTS idx_agg_user_state_year ON agg_user(state, year);
CREATE INDEX IF NOT EXISTS idx_map_tx_state_year ON map_transaction(state, year);
CREATE INDEX IF NOT EXISTS idx_top_tx_state_year ON top_transaction(state, year);
