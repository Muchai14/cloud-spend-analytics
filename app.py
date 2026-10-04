from pathlib import Path

import pandas as pd
import streamlit as st

# Configure the page
st.set_page_config(
    page_title="Cloud Spend Analytics",
    layout="wide"
)

st.title("Cloud Spend Analytics")
st.caption("Portfolio project using simulated cloud costs and budgets.")

# Load the monthly budget analysis
data_path = (
    Path(__file__).resolve().parent
    / "data"
    / "monthly_budget_variance.csv"
)

df = pd.read_csv(data_path, parse_dates=["month"])

# Let the user select a team
teams = ["All Teams"] + sorted(df["team"].unique().tolist())
selected_team = st.selectbox("Select a team", teams)

if selected_team == "All Teams":
    filtered_df = df.copy()
else:
    filtered_df = df[df["team"] == selected_team].copy()

# Calculate totals for the selected team across the full year
actual_cost = filtered_df["actual_cost_usd"].sum()
budget = filtered_df["budget_usd"].sum()
variance = actual_cost - budget

st.subheader("2025 Annual Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Actual Spend", f"${actual_cost:,.2f}")
col2.metric("Budget", f"${budget:,.2f}")
col3.metric("Budget Variance", f"${variance:,.2f}")

st.caption("Positive variance means over budget; negative means under budget.")

# Aggregate selected teams by month
monthly_trend = (
    filtered_df.groupby("month")[
        ["actual_cost_usd", "budget_usd"]
    ]
    .sum()
    .sort_index()
)

# Use readable labels for the chart
monthly_trend = monthly_trend.rename(
    columns={
        "actual_cost_usd": "Actual Spend (USD)",
        "budget_usd": "Budget (USD)"
    }
)

st.subheader("Monthly Spend vs Budget")
st.line_chart(monthly_trend)

# Calculate monthly variance across the selected teams
monthly_variance = (
    filtered_df.groupby("month")[
        ["actual_cost_usd", "budget_usd"]
    ]
    .sum()
    .sort_index()
)

monthly_variance["Budget Variance (USD)"] = (
    monthly_variance["actual_cost_usd"]
    - monthly_variance["budget_usd"]
)

# Format the monthly labels for display
monthly_variance.index = monthly_variance.index.strftime("%Y-%m")

st.subheader("Monthly Budget Variance")

st.bar_chart(
    monthly_variance[["Budget Variance (USD)"]]
)

st.caption(
    "Above zero = over budget. Below zero = under budget."
)
# Load daily costs to access service-level details
daily_cost_path = data_path.parent / "cloud_costs.csv"
daily_costs = pd.read_csv(
    daily_cost_path,
    parse_dates=["usage_date"]
)

# Apply the same team filter
if selected_team == "All Teams":
    selected_daily_costs = daily_costs.copy()
else:
    selected_daily_costs = daily_costs[
        daily_costs["team"] == selected_team
    ].copy()

# Calculate annual spending by service
service_costs = (
    selected_daily_costs.groupby("service")[["cost_usd"]]
    .sum()
    .rename(columns={"cost_usd": "Actual Spend (USD)"})
)

st.subheader("2025 Spend by Service")
st.bar_chart(service_costs)

st.caption(
    "Annual actual spending by service for the selected team(s)."
)

# Display the monthly records
st.subheader("Monthly Details")
st.dataframe(filtered_df, hide_index=True, use_container_width=True)

# Load detected anomalies from the simulated scenario
anomaly_path = data_path.parent / "scenario_anomalies.csv"
anomaly_df = pd.read_csv(
    anomaly_path,
    parse_dates=["usage_date"]
)

# Apply the existing team filter
if selected_team == "All Teams":
    selected_anomalies = anomaly_df.copy()
else:
    selected_anomalies = anomaly_df[
        anomaly_df["team"] == selected_team
    ].copy()

st.subheader("Anomaly Detection Demo")

st.caption(
    "Separate simulated scenario: one ML Compute charge was tripled. "
    "The spending and budget charts above use the original data."
)

st.write(
    "Detection rule: spending exceeds the prior eight same-weekday "
    "average by more than 30% and at least $50."
)

st.metric("Flagged Records", len(selected_anomalies))

if selected_anomalies.empty:
    st.info("No flagged records for the selected team.")
else:
    # Format a display copy while preserving the original values
    display_anomalies = selected_anomalies.copy()
    display_anomalies["usage_date"] = (
        display_anomalies["usage_date"].dt.strftime("%Y-%m-%d")
    )

    display_anomalies = display_anomalies.rename(
        columns={
            "usage_date": "Date",
            "team": "Team",
            "service": "Service",
            "cost_usd": "Actual Cost (USD)",
            "expected_cost_usd": "Expected Cost (USD)",
            "excess_cost_usd": "Above Baseline (USD)",
            "excess_pct": "Above Baseline (%)"
        }
    )

    st.dataframe(
        display_anomalies.round(2),
        hide_index=True,
        use_container_width=True
    )

st.caption(
    "A flag indicates spending that needs investigation; "
    "it does not establish waste or explain the cause."
)

# Load the December forecast evaluation
forecast_path = data_path.parent / "december_forecast_evaluation.csv"

forecast_df = pd.read_csv(
    forecast_path,
    parse_dates=["usage_date"]
)

# Apply the existing team filter
if selected_team == "All Teams":
    selected_forecast = forecast_df.copy()
else:
    selected_forecast = forecast_df[
        forecast_df["team"] == selected_team
    ].copy()

st.subheader("December 2025 Forecast Evaluation")

st.caption(
    "Historical evaluation using original simulated data. "
    "Predictions use only data available through November 30, 2025."
)

# Aggregate daily spending for the selected teams
forecast_chart = (
    selected_forecast.groupby("usage_date")[
        ["actual_cost_usd", "predicted_cost_usd"]
    ]
    .sum()
    .sort_index()
    .rename(columns={
        "actual_cost_usd": "Actual Spend (USD)",
        "predicted_cost_usd": "Predicted Spend (USD)"
    })
)

st.line_chart(forecast_chart)

# Calculate errors for the daily totals shown in the chart
daily_errors = (
    forecast_chart["Predicted Spend (USD)"]
    - forecast_chart["Actual Spend (USD)"]
).abs()

mae = daily_errors.mean()
actual_total = forecast_chart["Actual Spend (USD)"].sum()
wape = (
    daily_errors.sum() / actual_total * 100
    if actual_total > 0
    else None
)

col1, col2 = st.columns(2)
col1.metric("Daily MAE", f"${mae:,.2f}")
col2.metric("WAPE", f"{wape:.2f}%" if wape is not None else "N/A")

st.caption(
    "For All Teams, errors are calculated after combining daily costs. "
    "Overestimates and underestimates across teams may offset each other."
)

# Locate the saved report
report_path = (
    Path(__file__).resolve().parent
    / "reports"
    / "2025-12_cloud_spend_report.md"
)

st.subheader("AI-Assisted Monthly Report")

st.caption(
    "December 2025 | All Teams | Simulated data. "
    "Generated manually in an AI chat and checked against the input JSON. "
    "This saved report does not change with the team filter."
)

if report_path.exists():
    report_text = report_path.read_text(encoding="utf-8")
        # Use all teams for the fixed December report
    report_costs = df[
        df["month"] == pd.Timestamp("2025-12-01")
    ].copy()

    report_chart = (
        report_costs.set_index("team")[
            ["actual_cost_usd", "budget_usd"]
        ]
        .rename(columns={
            "actual_cost_usd": "Actual Spend (USD)",
            "budget_usd": "Budget (USD)"
        })
        .sort_index()
    )

    st.write("**December 2025 Spend vs Budget by Team**")

    st.bar_chart(
        report_chart,
        stack=False
    )
    
    with st.expander("Read the December report", expanded=True):
        # Escape dollar signs so currency is displayed as plain text
          st.markdown(report_text.replace("$", r"\$"))

    st.download_button(
        label="Download Report",
        data=report_text,
        file_name="2025-12_cloud_spend_report.md",
        mime="text/markdown"
    )
else:
    st.info("Save the December report in the reports folder to display it.")

# Offer the standalone report with its embedded chart
html_report_path = (
    Path(__file__).resolve().parent
    / "reports"
    / "2025-12_cloud_spend_report.html"
)

if html_report_path.exists():
    st.download_button(
        label="Download Report with Chart (HTML)",
        data=html_report_path.read_bytes(),
        file_name="2025-12_cloud_spend_report.html",
        mime="text/html",
        key="download_html_report"
    )
else:
    st.info("Run export_report.py to generate the HTML report.")