from pathlib import Path
import pandas as pd

# Generate the first day of each month
months = pd.date_range(
    start="2025-01-01",
    end="2025-12-01",
    freq="MS"
)

# Define assumed monthly budgets in USD
monthly_budgets = {
    "Engineering": 6200,
    "Data": 4100,
    "ML": 8200
}

rows = []

for month in months:
    for team, budget in monthly_budgets.items():
        rows.append({
            "month": month,
            "team": team,
            "budget_usd": budget
        })

df = pd.DataFrame(rows)

# Save the budget table
data_dir = Path(__file__).resolve().parent / "data"
data_dir.mkdir(parents=True, exist_ok=True)

output_path = data_dir / "monthly_budgets.csv"
df.to_csv(output_path, index=False, date_format="%Y-%m-%d")

print("First six records:")
print(df.head(6).to_string(index=False))
print("\nTotal rows:", len(df))
print(f"\nBudget data saved to: {output_path}")