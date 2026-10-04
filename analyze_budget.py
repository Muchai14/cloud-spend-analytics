from pathlib import Path
import duckdb

data_dir = Path(__file__).resolve().parent / "data"

con = duckdb.connect()

# Register the actual costs and budgets as SQL views
con.read_csv(
    str(data_dir / "monthly_team_costs.csv")
).create_view("monthly_costs")

con.read_csv(
    str(data_dir / "monthly_budgets.csv")
).create_view("monthly_budgets")

# Compare actual spending with the budget for each month and team
query = """
SELECT
    a.month,
    a.team,
    a.total_cost_usd AS actual_cost_usd,
    b.budget_usd,
    ROUND(
        a.total_cost_usd - b.budget_usd,
        2
    ) AS variance_usd,
    ROUND(
        (a.total_cost_usd - b.budget_usd)
        / NULLIF(b.budget_usd, 0) * 100,
        2
    ) AS variance_pct
FROM monthly_costs AS a
LEFT JOIN monthly_budgets AS b
    ON a.month = b.month
    AND a.team = b.team
ORDER BY a.month, a.team
"""

result = con.execute(query).df()

# Validate the join before saving
assert len(result) == 36, "Unexpected row count after joining."
assert not result["budget_usd"].isna().any(), "Missing budget matches."

output_path = data_dir / "monthly_budget_variance.csv"
result.to_csv(output_path, index=False, date_format="%Y-%m-%d")

print(result.to_string(index=False))
print("\nTotal rows:", len(result))
print(f"\nBudget analysis saved to: {output_path}")

con.close()