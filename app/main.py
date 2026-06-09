import os
import time
import logging
import joblib
import requests

from fastapi import FastAPI
from pydantic import BaseModel

from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response

from app.drift import DriftDetector


MODEL_PATH = os.getenv("MODEL_PATH", "model/model.joblib")
GITLAB_WEBHOOK_URL = os.getenv("GITLAB_WEBHOOK_URL", "")

app = FastAPI(title="AIOps Quality Project")

logging.basicConfig(level=logging.INFO)

request_counter = Counter(
    "prediction_requests_total",
    "Total prediction requests"
)

prediction_latency = Histogram(
    "prediction_latency_seconds",
    "Prediction latency"
)

drift_counter = Counter(
    "drift_events_total",
    "Total drift detection events"
)

model = None
drift_detector_service = DriftDetector()


@app.on_event("startup")
def load_model():
    global model

    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        logging.info("Model loaded")
    else:
        logging.warning("Model file not found")


class PredictionRequest(BaseModel):
    features: list[float]


def predict(features):
    prediction = model.predict([features])
    return int(prediction[0])


def trigger_retrain_pipeline():
    if not GITLAB_WEBHOOK_URL:
        logging.info("GitLab webhook URL is not configured. Retrain pipeline was not triggered.")
        return

    try:
        response = requests.post(GITLAB_WEBHOOK_URL, timeout=5)
        logging.info(f"Retrain pipeline trigger response: {response.status_code}")
    except Exception as error:
        logging.error(f"Failed to trigger retrain pipeline: {error}")


def detect_drift(features):
    is_drift = drift_detector_service.detect(features)

    if is_drift:
        drift_counter.inc()
        logging.warning("Drift detected")
        print("Drift detected")
        trigger_retrain_pipeline()

    return is_drift


@app.post("/predict")
def prediction(request: PredictionRequest):
    start_time = time.time()

    request_counter.inc()

    logging.info(f"Incoming request: {request.features}")

    detect_drift(request.features)

    result = predict(request.features)

    prediction_latency.observe(
        time.time() - start_time
    )

    return {
        "prediction": result
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type="text/plain"
    )
