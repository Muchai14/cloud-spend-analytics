from pathlib import Path
import pandas as pd

# Load the original costs for forecasting
data_dir = Path(__file__).resolve().parent / "data"
df = pd.read_csv(
    data_dir / "cloud_costs.csv",
    parse_dates=["usage_date"]
)

# Aggregate all services into daily spending for each team
daily_costs = (
    df.groupby(["usage_date", "team"], as_index=False)["cost_usd"]
    .sum()
    .sort_values(["team", "usage_date"])
    .reset_index(drop=True)
)

# Use January through November for training
# Reserve December for evaluating predictions
cutoff = pd.Timestamp("2025-12-01")

train = daily_costs[daily_costs["usage_date"] < cutoff].copy()
test = daily_costs[daily_costs["usage_date"] >= cutoff].copy()

print("Training period:")
print(
    train["usage_date"].min().date(),
    "to",
    train["usage_date"].max().date()
)
print("Training rows:", len(train))

print("\nTest period:")
print(
    test["usage_date"].min().date(),
    "to",
    test["usage_date"].max().date()
)
print("Test rows:", len(test))

# Use the final seven training days as the weekly pattern
last_week = train[
    train["usage_date"] >= cutoff - pd.Timedelta(days=7)
].copy()

last_week["day_of_week"] = last_week["usage_date"].dt.dayofweek

weekly_pattern = last_week[
    ["team", "day_of_week", "cost_usd"]
].rename(columns={"cost_usd": "predicted_cost_usd"})

# Create the forecast dates without using December actual costs
forecast_dates = pd.date_range(
    start="2025-12-01",
    end="2025-12-31",
    freq="D"
)

forecast = pd.MultiIndex.from_product(
    [forecast_dates, sorted(train["team"].unique())],
    names=["usage_date", "team"]
).to_frame(index=False)

forecast["day_of_week"] = forecast["usage_date"].dt.dayofweek

# Match each forecast date to the training week's weekday
forecast = forecast.merge(
    weekly_pattern,
    on=["team", "day_of_week"],
    how="left",
    validate="many_to_one"
)

assert not forecast["predicted_cost_usd"].isna().any(), (
    "Missing forecast values."
)

forecast = forecast[
    ["usage_date", "team", "predicted_cost_usd"]
].sort_values(["usage_date", "team"])

print("\nFirst nine predictions:")
print(forecast.head(9).round(2).to_string(index=False))
print("\nForecast rows:", len(forecast))

# Match predictions with December actual spending
evaluation = forecast.merge(
    test[["usage_date", "team", "cost_usd"]].rename(
        columns={"cost_usd": "actual_cost_usd"}
    ),
    on=["usage_date", "team"],
    how="left",
    validate="one_to_one"
)

assert not evaluation["actual_cost_usd"].isna().any(), (
    "Missing actual costs for evaluation."
)

# Measure the absolute error for each prediction
evaluation["absolute_error_usd"] = (
    evaluation["predicted_cost_usd"]
    - evaluation["actual_cost_usd"]
).abs()

# Calculate evaluation metrics for each team
metrics = evaluation.groupby("team").agg(
    mae_usd=("absolute_error_usd", "mean"),
    total_absolute_error_usd=("absolute_error_usd", "sum"),
    total_actual_cost_usd=("actual_cost_usd", "sum")
)

metrics["wape_pct"] = (
    metrics["total_absolute_error_usd"]
    / metrics["total_actual_cost_usd"].replace(0, float("nan"))
    * 100
)

print("\nDecember forecast accuracy by team:")
print(metrics[["mae_usd", "wape_pct"]].round(2).to_string())

# Save daily predictions, actual costs, and errors
evaluation_path = data_dir / "december_forecast_evaluation.csv"

evaluation.to_csv(
    evaluation_path,
    index=False,
    date_format="%Y-%m-%d"
)

# Save accuracy metrics and evaluation details
metrics_output = metrics[["mae_usd", "wape_pct"]].reset_index()
metrics_output["model"] = "Seasonal naive"
metrics_output["training_end"] = "2025-11-30"
metrics_output["test_start"] = "2025-12-01"
metrics_output["test_end"] = "2025-12-31"

metrics_path = data_dir / "forecast_metrics.csv"
metrics_output.to_csv(metrics_path, index=False)

print(f"\nForecast evaluation saved to: {evaluation_path}")
print(f"Forecast metrics saved to: {metrics_path}")