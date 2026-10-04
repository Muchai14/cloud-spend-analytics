import json
from pathlib import Path

import pandas as pd

data_dir = Path(__file__).resolve().parent / "data"

# Load the original monthly spending and budget analysis
df = pd.read_csv(
    data_dir / "monthly_budget_variance.csv",
    parse_dates=["month"]
)

# Prepare a report for December 2025
report_month = pd.Timestamp("2025-12-01")
monthly = df[df["month"] == report_month].copy()

assert len(monthly) == 3, "Expected three team records."
assert monthly["team"].nunique() == 3, "Expected three unique teams."
assert not monthly["budget_usd"].isna().any(), "Missing budgets."

# Calculate overall metrics from amounts, not team percentages
actual = float(monthly["actual_cost_usd"].sum())
budget = float(monthly["budget_usd"].sum())
variance = actual - budget

# Prepare each team's metrics
team_details = []

for _, row in monthly.sort_values("team").iterrows():
    team_details.append({
        "team": row["team"],
        "actual_cost_usd": round(float(row["actual_cost_usd"]), 2),
        "budget_usd": round(float(row["budget_usd"]), 2),
        "variance_usd": round(float(row["variance_usd"]), 2),
        "variance_pct": round(float(row["variance_pct"]), 2)
    })

report_data = {
    "report_month": "2025-12",
    "currency": "USD",
    "data_source": "Original simulated cloud costs and assumed budgets",
    "variance_definition": "Actual cost minus budget; positive means over budget",
    "actual_cost_usd": round(actual, 2),
    "budget_usd": round(budget, 2),
    "variance_usd": round(variance, 2),
    "variance_pct": (
        round(variance / budget * 100, 2)
        if budget > 0
        else None
    ),
    "team_details": team_details
}

# Save the input for a future AI-generated report
output_path = data_dir / "ai_report_input.json"
output_path.write_text(
    json.dumps(report_data, indent=2, allow_nan=False),
    encoding="utf-8"
)

print(json.dumps(report_data, indent=2, allow_nan=False))
print(f"\nReport input saved to: {output_path}")