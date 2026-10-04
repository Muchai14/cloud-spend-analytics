## Local Setup

Developed locally on macOS with Python 3.9.6.
Other environments have not yet been tested.

Open a terminal in the project folder.

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Generate data and analysis outputs

Run these commands in order:

```bash
python generate_data.py
python generate_budget.py
python analyze_costs.py
python analyze_budget.py
python validate_data.py
python create_anomaly_scenario.py
python detect_anomalies.py
python forecast_costs.py
python prepare_ai_report.py
```

The anomaly detector reads the separate simulated scenario.
The spending and forecast analyses use the original simulated data.

### 4. Export the saved report

Ensure the reviewed Markdown report exists at
`reports/2025-12_cloud_spend_report.md`, then run:

```bash
python export_report.py
```

The AI narrative was generated manually and saved in the repository.
The scripts do not generate or update the narrative automatically.
If the input data changes, regenerate and review the narrative
before exporting the report again.

### 5. Launch the dashboard

```bash
python -m streamlit run app.py
```

Open the Local URL printed in the terminal.
To stop the application, press Control+C in that terminal.

## Dashboard Preview

![Cloud spending dashboard showing annual spending, budget, and monthly trends](screenshots/dashboard-overview.png)