from pathlib import Path
import pandas as pd

# Load daily spending
data_dir = Path(__file__).resolve().parent / "data"
df = pd.read_csv(
    data_dir / "cloud_costs_scenario.csv",
    parse_dates=["usage_date"]
)

df = df.sort_values(
    ["team", "service", "usage_date"]
).reset_index(drop=True)

# Monday = 0, Sunday = 6
df["day_of_week"] = df["usage_date"].dt.dayofweek

# Use only earlier observations from the same weekday
df["expected_cost_usd"] = (
    df.groupby(["team", "service", "day_of_week"])["cost_usd"]
    .transform(
        lambda values: values.shift(1).rolling(
            window=8,
            min_periods=8
        ).mean()
    )
)

# Display recent results for one team and service
sample = df[
    (df["team"] == "ML")
    & (df["service"] == "Compute")
].tail(10)

print(
    sample[
        ["usage_date", "team", "service",
         "cost_usd", "expected_cost_usd"]
    ].round(2).to_string(index=False)
)

print(
    "\nRecords without enough history:",
    df["expected_cost_usd"].isna().sum()
)

# Calculate spending above the historical baseline
df["excess_cost_usd"] = (
    df["cost_usd"] - df["expected_cost_usd"]
)

# Avoid division by zero when calculating percentage changes
baseline = df["expected_cost_usd"].replace(0, float("nan"))

df["excess_pct"] = (
    df["excess_cost_usd"] / baseline * 100
)

# Flag high spending only when enough history is available
df["is_anomaly"] = (
    df["expected_cost_usd"].notna()
    & (df["excess_pct"] > 30)
    & (df["excess_cost_usd"] >= 50)
)

anomalies = df.loc[
    df["is_anomaly"],
    [
        "usage_date",
        "team",
        "service",
        "cost_usd",
        "expected_cost_usd",
        "excess_cost_usd",
        "excess_pct"
    ]
]

print("\nAnomalies detected:", len(anomalies))

if anomalies.empty:
    print("No spending spikes met the current thresholds.")
else:
    print(anomalies.round(2).to_string(index=False))


# Save flagged records from the simulated scenario
output_path = data_dir / "scenario_anomalies.csv"

anomalies.to_csv(
    output_path,
    index=False,
    date_format="%Y-%m-%d"
)

print(f"\nScenario anomalies saved to: {output_path}")