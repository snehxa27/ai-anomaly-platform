# AI Anomaly Platform

Production-oriented starter structure for building an AI-powered anomaly detection system with offline training, optional streaming ingestion, alerting, and an API layer.

## Folder structure

```
ai-anomaly-platform/
├── data/              # Raw and processed datasets
├── models/            # Saved ML/DL models
├── training/          # Model training scripts
├── streaming/         # Streaming ingestion (optional)
├── backend/           # Flask API backend
├── database/          # PostgreSQL connection scripts
├── alerts/            # Alert logic (email/slack triggers)
├── dashboard/         # Visualization dashboard
└── main.py            # Application entry point
```

## Setup

### 1) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Expected output:

```
AI Anomaly Platform Initialized
```

## Offline model training (no streaming)

Train an anomaly model from a CSV (numeric columns are used automatically):

```bash
python main.py train-offline --data data/your_dataset.csv
```

Artifacts are saved with `joblib` under `models/` by default.

