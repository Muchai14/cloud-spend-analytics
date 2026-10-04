from pathlib import Path
import pandas as pd

# Load the saved CSV and parse the date column
file_path = (
    Path(__file__).resolve().parent
    / "data"
    / "cloud_costs.csv"
)

df = pd.read_csv(file_path, parse_dates=["usage_date"])

# Check for missing values in each column
print("Missing values:")
print(df.isna().sum())

# Each date-team-service combination should appear once
duplicate_count = df.duplicated(
    subset=["usage_date", "team", "service"]
).sum()
print("\nDuplicate records:", duplicate_count)

# Costs should never be negative
negative_count = (df["cost_usd"] < 0).sum()
print("Negative costs:", negative_count)

# Check the number of records and the date range
print("\nTotal rows:", len(df))
print("Start date:", df["usage_date"].min().date())
print("End date:", df["usage_date"].max().date())

# Load the monthly analysis
monthly_path = file_path.parent / "monthly_budget_variance.csv"
monthly_df = pd.read_csv(monthly_path)

# Reconcile daily and monthly spending for each team
daily_totals = df.groupby("team")["cost_usd"].sum()
monthly_totals = monthly_df.groupby("team")["actual_cost_usd"].sum()

comparison = pd.concat(
    [
        daily_totals.rename("daily_total_usd"),
        monthly_totals.rename("monthly_total_usd")
    ],
    axis=1
)

comparison["difference_usd"] = (
    comparison["daily_total_usd"]
    - comparison["monthly_total_usd"]
).round(2)

print("\nDaily vs monthly reconciliation:")
print(comparison.round(2).to_string())

assert not comparison.isna().any().any(), "Team mismatch between datasets."
assert (comparison["difference_usd"] == 0).all(), "Cost totals do not match."

print("\nReconciliation passed.")