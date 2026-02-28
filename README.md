

# 📄 README.md

```markdown
# 🏥 AI-Driven Healthcare Anomaly Detection System

A real-time AI-powered healthcare monitoring platform that detects abnormal patterns in patient vital signs and generates early risk alerts using Machine Learning.

---

## 📌 Project Overview

The AI-Driven Healthcare Anomaly Detection System is an end-to-end real-time monitoring and decision-support platform designed to detect abnormal physiological patterns in patient vitals.

Unlike traditional static threshold-based systems, this platform uses Machine Learning models such as Isolation Forest to dynamically identify anomalies in live healthcare data streams.

The system integrates:

- Real-time data streaming
- Machine learning anomaly detection
- Severity classification (LOW, MEDIUM, HIGH)
- PostgreSQL database storage
- Flask-based interactive dashboard
- Automated email alert system
- Docker-based deployment

---

## 🚀 Features

- 📡 Real-time patient vital monitoring
- 🤖 ML-based anomaly detection (Isolation Forest)
- ⚠ Severity classification (LOW / MEDIUM / HIGH)
- 📊 Live dashboard visualization
- 📧 Automatic email alerts for critical cases
- 🗄 Persistent database storage (PostgreSQL)
- 🐳 Docker containerization support

---

## 🏗 System Architecture

Data Flow:

Patient Vitals → Producer → Kafka → Consumer → ML Model →  
Severity Classification → Database → Dashboard → Email Alerts

---

## 🛠 Tech Stack

| Component | Technology |
|------------|------------|
| Programming Language | Python |
| Backend Framework | Flask |
| Machine Learning | Scikit-learn |
| Streaming | Apache Kafka |
| Database | PostgreSQL |
| Visualization | HTML, CSS, JavaScript |
| Containerization | Docker |
| Email Alerts | SMTP |

---

## 📂 Project Structure

```

ai-anomaly-platform/
│
├── backend/           # Flask backend
├── dashboard/         # Dashboard UI
├── streaming/         # Kafka producer & consumer
├── training/          # Model training modules
├── models/            # Saved ML models
├── database/          # DB configuration
├── alerts/            # Email alert logic
├── utils/             # Utility functions
│
├── docker-compose.yml
├── requirements.txt
└── README.md

```

---

## ⚙ Installation & Setup

### 1️⃣ Clone Repository

```

git clone [https://github.com/snehxa27/ai-anomaly-platform.git](https://github.com/snehxa27/ai-anomaly-platform.git)
cd ai-anomaly-platform

```

---

### 2️⃣ Create Virtual Environment

```

python -m venv venv
source venv/bin/activate   # Mac/Linux

```

---

### 3️⃣ Install Dependencies

```

pip install -r requirements.txt

```

---

### 4️⃣ Configure Environment Variables

Create a `.env` file:

```

EMAIL_USER=your_email
EMAIL_PASSWORD=your_password
DATABASE_URL=your_db_url

```

---

### 5️⃣ Run with Docker (Recommended)

```

docker-compose up --build

```

OR run services manually.

---

## 📊 Results

The system successfully:

- Detected abnormal heart rate spikes
- Identified low oxygen saturation events
- Classified anomalies into severity levels
- Triggered automatic email alerts for HIGH severity
- Displayed real-time visualization on dashboard
- Stored all records in PostgreSQL

---

## 📈 Example High-Risk Detection

- Heart Rate: 134 bpm  
- SpO₂: 88%  
- Temperature: 38.4°C  
- Blood Pressure: 158 mmHg  
- Severity: HIGH  

---

## 🔍 Performance

- Average processing time per record: ~1 second
- Real-time dashboard updates
- Stable streaming performance

---

## 🔮 Future Scope

- Deep learning Autoencoder integration
- Cloud deployment (AWS / GCP)
- Multi-patient monitoring
- Mobile application integration
- Integration with hospital EMR systems

---

## 👩‍💻 Author

Sneha Karande  
Bachelor’s in Data Science  

