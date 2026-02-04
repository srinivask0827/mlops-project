from fastapi import FastAPI, HTTPException
import os
import mlflow
import mlflow.pyfunc
import pandas as pd
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response
import time


app = FastAPI()

REQUEST_COUNT = Counter("request_count", "Total API Requests")
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency")


TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://192.168.1.34:5000")
MODEL_URI = os.getenv("MODEL_URI", "runs:/bcd326f049644e13988f292858794df3/model")

mlflow.set_tracking_uri(TRACKING_URI)

model = None
model_error = None

@app.on_event("startup")
def load_model():
    global model, model_error
    try:
        model = mlflow.pyfunc.load_model(MODEL_URI)
        model_error = None
        print("✅ Model loaded successfully")
    except Exception as e:
        model = None
        model_error = str(e)
        print(f"❌ Model load failed: {model_error}")

@app.get("/")
def home():
    return {
        "message": "ML API Running",
        "tracking_uri": TRACKING_URI,
        "model_uri": MODEL_URI,
        "model_loaded": model is not None,
        "model_error": model_error
    }

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")


@app.post("/predict")
def predict(hours: float):
    REQUEST_COUNT.inc()
    start_time = time.time()

    data = pd.DataFrame([[hours]], columns=["hours"])
    prediction = model.predict(data)[0]
    result = "Pass" if prediction == 1 else "Fail"

    REQUEST_LATENCY.observe(time.time() - start_time)

    return {"result": result}
