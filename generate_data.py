import pandas as pd
#Generate one date per day for the entire year
dates = pd.date_range(start="2025-01-01",
                       end="2025-12-31", freq="D")
#Define three teams and three cloud service catagories

teams = ["Engineering", "Data", "ML"]
services = ["Compute", "Storage", "Network"]

print("Number of days:", len(dates))
print("First five dates:")
print(dates[:5])

print("Teams:", teams)
print("Services:", services)

import numpy as np

# Use a fixed seed to make the results reproducible
rng = np.random.default_rng(seed=42)

# Define assumed daily costs in USD for each service
base_daily_cost = {
    "Compute": 100,
    "Storage": 30,
    "Network": 15
}

# Represent differences in usage across teams
team_multiplier = {
    "Engineering": 1.5,
    "Data": 1.0,
    "ML": 2.0
}

rows = []

for date in dates:
    for team in teams:
        for service in services:
            # Reduce compute spending on weekends
            weekend_factor = (
                0.6
                if date.dayofweek >= 5 and service == "Compute"
                else 1.0
            )

            # Add random daily variation between -10% and +10%
            variation = rng.uniform(0.9, 1.1)

            cost = (
                base_daily_cost[service]
                * team_multiplier[team]
                * weekend_factor
                * variation
            )

            rows.append({
                "usage_date": date,
                "team": team,
                "service": service,
                "cost_usd": round(cost, 2)
            })

# Convert the records into a table
df = pd.DataFrame(rows)

print("\nFirst five records:")
print(df.head())

print("\nTotal rows:", len(df))

from pathlib import Path

# Create a data folder next to this script
data_dir = Path(__file__).resolve().parent / "data"
data_dir.mkdir(parents=True, exist_ok=True)

# Save the simulated costs without the DataFrame index
output_path = data_dir / "cloud_costs.csv"
df.to_csv(output_path, index=False, date_format="%Y-%m-%d")

print(f"\nData saved to: {output_path}")

