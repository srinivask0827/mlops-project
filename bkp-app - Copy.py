from fastapi import FastAPI
import os
import mlflow
import mlflow.pyfunc
import pandas as pd

app = FastAPI()

# Read tracking URI from environment variable (best for Docker)
# Example for Docker: http://192.168.1.34:5000
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Load model from MLflow run
RUN_ID = "bcd326f049644e13988f292858794df3"
MODEL_URI = f"runs:/{RUN_ID}/model"

model = mlflow.pyfunc.load_model(MODEL_URI)

@app.get("/")
def home():
    return {
        "message": "ML API Running",
        "mlflow_tracking_uri": MLFLOW_TRACKING_URI,
        "model_uri": MODEL_URI
    }

@app.post("/predict")
def predict(hours: float):
    data = pd.DataFrame([[hours]], columns=["hours"])
    prediction = model.predict(data)[0]
    result = "Pass" if int(prediction) == 1 else "Fail"
    return {"result": result}
