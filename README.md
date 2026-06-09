# AIOps Quality Project

## Overview

This project demonstrates an end-to-end AIOps and MLOps workflow using:

* FastAPI
* Machine Learning Model
* Drift Detection
* Prometheus
* Grafana
* Loki / Promtail
* GitLab CI
* Helm
* ArgoCD
* Kubernetes

The system performs online inference, monitors model behavior, detects potential data drift, and supports automated retraining workflows.

---

## Project Structure

```text
aiops-quality-project/
├── app/
│   └── main.py
├── model/
│   ├── train.py
│   └── model.joblib
├── helm/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       └── service.yaml
├── argocd/
│   └── application.yaml
├── grafana/
│   └── dashboards.json
├── prometheus/
│   └── additionalScrapeConfigs.yaml
├── Dockerfile
├── requirements.txt
├── .gitlab-ci.yml
└── README.md
```

---

## Architecture

### FastAPI Service

The FastAPI application:

* Loads the model during startup
* Accepts prediction requests
* Logs incoming requests
* Detects drift conditions
* Exposes Prometheus metrics

Endpoints:

| Endpoint | Description        |
| -------- | ------------------ |
| /health  | Health check       |
| /predict | Model inference    |
| /metrics | Prometheus metrics |

---

## Model Training

Training script:

```bash
python model/train.py
```

The script:

* Loads Iris dataset
* Trains RandomForestClassifier
* Saves model to:

```text
model/model.joblib
```

---

## Running Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Train model:

```bash
python model/train.py
```

Run API:

```bash
uvicorn app.main:app --reload
```

---

## Testing Prediction

Example request:

```bash
curl -X POST http://localhost:8000/predict \
-H "Content-Type: application/json" \
-d '{"features":[5.1,3.5,1.4,0.2]}'
```

Example response:

```json
{
  "prediction": 0
}
```

---

## Drift Detection

The application includes a simple drift detector.

Example:

```json
{
  "features":[10,10,10,10]
}
```

When drift is detected:

```text
WARNING: Drift detected
```

appears in application logs.

---

## Logging

Application logs are written to stdout.

Example:

```text
Incoming request: [10.0,10.0,10.0,10.0]
WARNING: Drift detected
```

Logs are collected by Promtail and stored in Loki.

---

## Prometheus Metrics

Metrics endpoint:

```text
/metrics
```

Available metrics:

```text
prediction_requests_total
prediction_latency_seconds
```

---

## Grafana Dashboard

Dashboard panels:

* Prediction Requests Total
* Prediction Latency
* Drift Detection Events

Grafana visualizes service performance and model activity.

---

## Helm Deployment

Deploy chart:

```bash
helm install aiops-quality-project ./helm
```

Configuration:

* Image repository
* Image tag
* Service port
* Environment variables

are managed through:

```text
helm/values.yaml
```

---

## ArgoCD

Application manifest:

```text
argocd/application.yaml
```

Features:

* Auto Sync
* Self Heal
* Namespace Auto Creation

ArgoCD continuously synchronizes Kubernetes resources with Git.

---

## GitLab CI

Pipeline stages:

### Retrain Model

```bash
python model/train.py
```

Produces:

```text
model/model.joblib
```

### Build Image

```bash
docker build -t aiops-quality-project .
```

Pipeline can be triggered manually or by drift detection events.

---

## Updating the Model

1. Modify training logic.
2. Run retrain pipeline.
3. Generate new model artifact.
4. Build new Docker image.
5. Commit changes.
6. ArgoCD automatically redeploys the application.

---

## Verification Checklist

### API

* [x] Health endpoint works
* [x] Prediction endpoint works
* [x] Metrics endpoint works

### Drift Detection

* [x] Drift warning appears in logs

### Monitoring

* [x] Metrics exposed to Prometheus
* [x] Dashboard configured for Grafana

### CI/CD

* [x] Retrain pipeline configured
* [x] Docker build configured
* [x] ArgoCD auto-sync enabled

### Kubernetes

* [x] Helm chart created
* [x] Service configured
* [x] Deployment configured
