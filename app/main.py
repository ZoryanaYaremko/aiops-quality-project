import os
import time
import logging
import joblib
import numpy as np

from fastapi import FastAPI
from pydantic import BaseModel

from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response


MODEL_PATH = "model/model.joblib"

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


model = None


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


def drift_detector(features):
    """
    Mock drift detector.
    """

    if np.mean(features) > 5:
        logging.warning("Drift detected")
        print("Drift detected")
        return True

    return False


@app.post("/predict")
def prediction(request: PredictionRequest):

    start_time = time.time()

    request_counter.inc()

    logging.info(f"Incoming request: {request.features}")

    drift_detector(request.features)

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