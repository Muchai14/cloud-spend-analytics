import base64
from io import BytesIO
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import markdown
import numpy as np
import pandas as pd

project_dir = Path(__file__).resolve().parent
reports_dir = project_dir / "reports"

# Load December spending for all teams
df = pd.read_csv(
    project_dir / "data" / "monthly_budget_variance.csv",
    parse_dates=["month"]
)

monthly = (
    df[df["month"] == pd.Timestamp("2025-12-01")]
    .sort_values("team")
    .reset_index(drop=True)
)

assert len(monthly) == 3, "Expected three team records."
assert monthly["team"].nunique() == 3, "Expected three unique teams."

# Create a grouped bar chart
plt.rcParams.update({"font.size": 11})

fig, ax = plt.subplots(figsize=(9, 4.5), layout="constrained")

positions = np.arange(len(monthly))
width = 0.35

actual_bars = ax.bar(
    positions - width / 2,
    monthly["actual_cost_usd"],
    width,
    label="Actual Spend",
    color="#2563EB"
)

budget_bars = ax.bar(
    positions + width / 2,
    monthly["budget_usd"],
    width,
    label="Budget",
    color="#CBD5E1"
)

ax.set_xticks(positions)
ax.set_xticklabels(monthly["team"])
ax.set_ylabel("USD")
ax.set_title("December 2025 Spend vs Budget by Team", pad=18)
ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
ax.set_ylim(0, monthly[["actual_cost_usd", "budget_usd"]].max().max() * 1.22)

ax.bar_label(actual_bars, fmt="%.2f", padding=4, fontsize=9)
ax.bar_label(budget_bars, fmt="%.2f", padding=4, fontsize=9)

ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.2)
ax.set_axisbelow(True)
ax.legend(frameon=False)

# Embed the chart so the HTML needs no separate image file
buffer = BytesIO()
fig.savefig(buffer, format="png", dpi=160)
plt.close(fig)

chart_base64 = base64.b64encode(buffer.getvalue()).decode("ascii")

# Convert the saved Markdown report into HTML
report_text = (
    reports_dir / "2025-12_cloud_spend_report.md"
).read_text(encoding="utf-8")

report_body = markdown.markdown(
    report_text,
    extensions=["tables"]
)

# Build a standalone report
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>December 2025 Cloud Spend Review</title>
<style>
    body {{
        font-family: Arial, sans-serif;
        color: #172033;
        background: #f1f5f9;
        margin: 0;
        padding: 32px 16px;
        line-height: 1.65;
    }}
    main {{
        max-width: 960px;
        margin: auto;
        background: white;
        padding: 40px;
        border-radius: 12px;
    }}
    h1 {{ margin-bottom: 8px; line-height: 1.2; }}
    h3 {{ margin-top: 32px; }}
    .subtitle {{ color: #526075; }}
    figure {{ margin: 32px 0; }}
    img {{ width: 100%; height: auto; }}
    figcaption {{ color: #526075; font-size: 14px; }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }}
    th, td {{
        padding: 10px;
        border-bottom: 1px solid #dbe2ea;
    }}
    th {{ background: #eff6ff; }}
    @media (max-width: 600px) {{
        main {{ padding: 20px; }}
        table {{ display: block; overflow-x: auto; }}
    }}
    @media print {{
        body {{ background: white; padding: 0; }}
        main {{ padding: 0; max-width: none; }}
        figure, table {{ break-inside: avoid; }}
    }}
</style>
</head>
<body>
<main>
    <h1>December 2025 Cloud Spend Review</h1>
    <p class="subtitle">
        All Teams | Simulated Data | AI-assisted narrative reviewed
        against source metrics
    </p>

    <figure>
        <img
            src="data:image/png;base64,{chart_base64}"
            alt="December actual spending and budget for Data,
                 Engineering, and ML. All three teams exceeded budget."
        >
        <figcaption>
            Source: simulated monthly spending and assumed budgets.
            Exact differences are shown in the table below.
        </figcaption>
    </figure>

    {report_body}
</main>
</body>
</html>
"""

output_path = reports_dir / "2025-12_cloud_spend_report.html"
output_path.write_text(html, encoding="utf-8")

print(f"HTML report saved to: {output_path}")