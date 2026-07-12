-- sql_queries.sql
-- Sample analytical queries run against processed/phonepe.db
-- Run with: sqlite3 processed/phonepe.db < sql_queries.sql

-- 1. Top 5 states by total transaction value
SELECT state, ROUND(SUM(amount)/1e12, 2) AS amount_in_trillion
FROM agg_transaction
GROUP BY state
ORDER BY amount_in_trillion DESC
LIMIT 5;

-- 2. Year-over-year transaction growth (national)
SELECT year, ROUND(SUM(amount)/1e12, 2) AS total_amount_trillion
FROM agg_transaction
GROUP BY year
ORDER BY year;

-- 3. Device brand market share among registered users
SELECT brand, SUM(count) AS users,
       ROUND(100.0 * SUM(count) / (SELECT SUM(count) FROM agg_user), 1) AS pct_share
FROM agg_user
GROUP BY brand
ORDER BY users DESC;

-- 4. Top 5 districts by transaction amount
SELECT entity AS district, ROUND(SUM(amount)/1e12, 2) AS amount_trillion
FROM top_transaction
WHERE level = 'district'
GROUP BY entity
ORDER BY amount_trillion DESC
LIMIT 5;

-- 5. Insurance-to-transaction penetration ratio by state (lowest = growth opportunity)
SELECT t.state,
       ROUND(100.0 * SUM(i.amount) / SUM(t.amount), 4) AS insurance_penetration_pct
FROM map_transaction t
JOIN map_insurance i
  ON t.state = i.state AND t.year = i.year AND t.quarter = i.quarter
GROUP BY t.state
ORDER BY insurance_penetration_pct ASC
LIMIT 5;

-- 6. App engagement: opens per registered user by year
SELECT year,
       SUM(app_opens) AS total_opens,
       SUM(registered_users) AS total_users,
       ROUND(1.0 * SUM(app_opens) / SUM(registered_users), 2) AS opens_per_user
FROM map_user
GROUP BY year
ORDER BY year;

-- 7. Window function: rank states within each year by transaction amount
SELECT year, state, amount, state_rank
FROM (
    SELECT
        year,
        state,
        amount,
        RANK() OVER (PARTITION BY year ORDER BY amount DESC) AS state_rank
    FROM (
        SELECT
            year,
            state,
            SUM(amount) AS amount
        FROM agg_transaction
        GROUP BY year, state
    ) ranked_amounts
) ranked_states
WHERE state_rank <= 3
ORDER BY year, state_rank;

-- 8. CTE + LAG: quarter-over-quarter growth rate, national level
WITH quarterly AS (
    SELECT year, quarter, SUM(amount) AS amount
    FROM agg_transaction
    GROUP BY year, quarter
)
SELECT year, quarter, amount,
       ROUND(100.0 * (amount - LAG(amount) OVER (ORDER BY year, quarter))
             / LAG(amount) OVER (ORDER BY year, quarter), 1) AS qoq_growth_pct
FROM quarterly
ORDER BY year, quarter;

-- 9. HAVING: states whose average quarterly transaction value exceeds the national average
SELECT state, ROUND(AVG(amount), 0) AS avg_quarterly_amount
FROM agg_transaction
GROUP BY state
HAVING AVG(amount) > (SELECT AVG(amount) FROM agg_transaction)
ORDER BY avg_quarterly_amount DESC;

-- 10. CASE: bucket states into growth tiers based on 2024 vs 2020 transaction amount
WITH by_state_year AS (
    SELECT state, year, SUM(amount) AS amount
    FROM agg_transaction
    WHERE year IN (2020, 2024)
    GROUP BY state, year
),
pivoted AS (
    SELECT state,
           MAX(CASE WHEN year = 2020 THEN amount END) AS amt_2020,
           MAX(CASE WHEN year = 2024 THEN amount END) AS amt_2024
    FROM by_state_year
    GROUP BY state
)
SELECT state,
       ROUND(100.0 * (amt_2024 - amt_2020) / amt_2020, 1) AS growth_pct,
       CASE
           WHEN (amt_2024 - amt_2020) / amt_2020 >= 5 THEN 'High Growth'
           WHEN (amt_2024 - amt_2020) / amt_2020 >= 2 THEN 'Moderate Growth'
           ELSE 'Low Growth'
       END AS growth_tier
FROM pivoted
ORDER BY growth_pct DESC;
