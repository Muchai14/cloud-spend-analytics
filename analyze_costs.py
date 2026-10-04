from pathlib import Path
import duckdb

# Locate the CSV file
file_path = (
    Path(__file__).resolve().parent
    / "data"
    / "cloud_costs.csv"
)

# Create an in-memory database and load the CSV
con = duckdb.connect()
con.read_csv(str(file_path)).create_view("cloud_costs")

# Calculate monthly spending by team
query = """
WITH monthly_costs AS (
    SELECT
        DATE_TRUNC('month', CAST(usage_date AS DATE)) AS month,
        team,
        SUM(cost_usd) AS total_cost_usd
    FROM cloud_costs
    GROUP BY 1, 2
),
previous_costs AS (
    SELECT
        month,
        team,
        total_cost_usd,
        LAG(total_cost_usd) OVER (
            PARTITION BY team
            ORDER BY month
        ) AS previous_month_cost_usd
    FROM monthly_costs
)
SELECT
    month,
    team,
    ROUND(total_cost_usd, 2) AS total_cost_usd,
    ROUND(previous_month_cost_usd, 2) AS previous_month_cost_usd,
    ROUND(
        (total_cost_usd - previous_month_cost_usd)
        / NULLIF(previous_month_cost_usd, 0) * 100,
        2
    ) AS mom_change_pct
FROM previous_costs
ORDER BY month, team
"""

result = con.execute(query).df()

print(result.to_string(index=False))
print("\nTotal rows:", len(result))

# Save the monthly analysis next to the source CSV
output_path = file_path.parent / "monthly_team_costs.csv"

result.to_csv(
    output_path,
    index=False,
    date_format="%Y-%m-%d"
)

print(f"\nMonthly analysis saved to: {output_path}")

con.close()