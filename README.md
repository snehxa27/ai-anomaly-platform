# 🏥 AI-Driven Healthcare Anomaly Detection System

Real-time AI-powered healthcare monitoring platform that detects abnormal patient vital patterns and generates automated health risk alerts using Machine Learning.

---

## 📌 Overview

This system continuously monitors:

- Heart Rate  
- SpO₂  
- Temperature  
- Blood Pressure  

Using **Isolation Forest**, it classifies patient conditions into:

- 🟢 LOW  
- 🟡 MEDIUM  
- 🔴 HIGH  

Integrated with Kafka streaming, PostgreSQL storage, dashboard visualization, and automated email alerts.

---

## 🚀 Features

- Real-time data streaming (Kafka)
- ML-based anomaly detection
- Severity classification
- Live dashboard
- Email alerts for critical cases
- PostgreSQL storage
- Dockerized deployment

---

## 🛠 Tech Stack

- **Backend:** Python, Flask  
- **ML:** Scikit-learn (Isolation Forest)  
- **Streaming:** Apache Kafka  
- **Database:** PostgreSQL  
- **Frontend:** HTML, CSS, JS  
- **Deployment:** Docker  

---

## 📂 Project Structure
## 📂 Project Structure

```text
ai-anomaly-platform/
│
├── backend/            # Flask backend services
│   ├── app.py
│   └── main.py
│
├── dashboard/          # Frontend dashboard (UI)
│   └── index.html
│
├── streaming/          # Kafka producer & consumer
│   ├── producer.py
│   └── consumer.py
│
├── training/           # Model training & preprocessing
├── models/             # Saved ML models (.pkl files)
├── database/           # PostgreSQL configuration
├── alerts/             # Email alert system
├── utils/              # Helper utilities
│
├── docker-compose.yml  # Container orchestration
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## ⚙ Setup

```bash
git clone https://github.com/snehxa27/ai-anomaly-platform.git
cd ai-anomaly-platform
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker-compose up --build

📊 Results

Detected abnormal heart rate spikes

Identified low oxygen levels

Classified LOW / MEDIUM / HIGH severity

Triggered email alerts

Stored records in PostgreSQL

Real-time dashboard updates

👩‍💻 Author

Sneha Karande
B.Tech Data Science
