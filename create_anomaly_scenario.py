from pathlib import Path
import pandas as pd

data_dir = Path(__file__).resolve().parent / "data"

# Load the original data
df = pd.read_csv(
    data_dir / "cloud_costs.csv",
    parse_dates=["usage_date"]
)

# Select exactly one record for the simulated spike
mask = (
    (df["usage_date"] == pd.Timestamp("2025-09-15"))
    & (df["team"] == "ML")
    & (df["service"] == "Compute")
)

assert mask.sum() == 1, "Expected exactly one matching record."

original_cost = df.loc[mask, "cost_usd"].iloc[0]

# Triple the cost to simulate a spending spike
df.loc[mask, "cost_usd"] = (
    df.loc[mask, "cost_usd"] * 3
).round(2)

updated_cost = df.loc[mask, "cost_usd"].iloc[0]

# Save a separate scenario without changing the original CSV
output_path = data_dir / "cloud_costs_scenario.csv"
df.to_csv(output_path, index=False, date_format="%Y-%m-%d")

print("Scenario: ML Compute spending spike on 2025-09-15")
print(f"Original cost: ${original_cost:.2f}")
print(f"Updated cost: ${updated_cost:.2f}")
print(f"Scenario saved to: {output_path}")