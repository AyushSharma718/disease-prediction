 # ================================================================
# Disease Prediction API
# Built with FastAPI
# ================================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import numpy as np
import pandas as pd
import joblib
import json
import os

# ----------------------------------------------------------------
# Load model and metadata ONCE when server starts
# We load outside of functions so it loads only once
# not on every single request (that would be slow)
# ----------------------------------------------------------------

# Get the directory where this file lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Go one level up to project root, then into models/
MODELS_DIR = os.path.join(BASE_DIR, '..', 'models')

# Load the full pipeline (preprocessor + model combined)
pipeline = joblib.load(os.path.join(MODELS_DIR, 'full_pipeline.joblib'))

# Load metadata
with open(os.path.join(MODELS_DIR, 'model_metadata.json'), 'r') as f:
    metadata = json.load(f)

# Columns that cannot be zero medically
ZERO_COLUMNS = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']

# ----------------------------------------------------------------
# Create FastAPI app
# ----------------------------------------------------------------
app = FastAPI(
    title       = "Disease Prediction API",
    description = "Predicts diabetes risk using a trained Random Forest model",
    version     = "1.0.0",
    docs_url    = "/docs"   # Swagger UI available at /docs
)

# ----------------------------------------------------------------
# CORS Middleware
# CORS = Cross Origin Resource Sharing
# This allows our frontend (running on different port) to talk to API
# Without this, browser blocks requests from frontend to backend
# ----------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],  # allow all origins (restrict in production)
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ----------------------------------------------------------------
# Input Schema (Pydantic Model)
# Pydantic automatically:
#   1. Validates that all required fields are present
#   2. Validates that values are correct data types
#   3. Returns clear error messages if validation fails
#   4. Documents the API automatically in Swagger UI
# ----------------------------------------------------------------
class PatientData(BaseModel):
    Pregnancies              : int = Field(
        ...,
        ge=0,
        le=20,
        description="Number of pregnancies (0-20)"
    )

    Glucose                  : Optional[float] = Field(
        ...,
        ge=0,
        le=300,
        description="Plasma glucose concentration (mg/dL)"
    )

    BloodPressure            : Optional[float] = Field(
        ...,
        ge=0,
        le=200,
        description="Diastolic blood pressure (mmHg)"
    )

    SkinThickness            : Optional[float] = Field(
        ...,
        ge=0,
        le=100,
        description="Tricep skin fold thickness (mm)"
    )

    Insulin                  : Optional[float] = Field(
        ...,
        ge=0,
        le=900,
        description="2-hour serum insulin (mu U/ml)"
    )

    BMI                      : Optional[float] = Field(
        ...,
        ge=0,
        le=70,
        description="Body mass index (kg/m²)"
    )

    DiabetesPedigreeFunction : float = Field(
        ...,
        ge=0,
        le=3,
        description="Diabetes pedigree function score"
    )

    Age                      : int = Field(
        ...,
        ge=1,
        le=120,
        description="Age in years"
    )

    @field_validator(
        'Glucose',
        'BloodPressure',
        'SkinThickness',
        'Insulin',
        'BMI',
        mode='before'
    )
    @classmethod
    def zero_means_missing(cls, value):
        """
        Zeros in these fields are medically impossible.
        We convert them to None so the pipeline can impute them.
        """
        if value == 0:
            return None

        return value

    class Config:
        # Show example values in Swagger docs
        json_schema_extra = {
            "example": {
                "Pregnancies": 6,
                "Glucose": 148,
                "BloodPressure": 72,
                "SkinThickness": 35,
                "Insulin": 0,
                "BMI": 33.6,
                "DiabetesPedigreeFunction": 0.627,
                "Age": 50
            }
        }

# ----------------------------------------------------------------
# Response Schema
# Defines exactly what our API returns
# ----------------------------------------------------------------
class PredictionResponse(BaseModel):
    prediction          : int
    prediction_label    : str
    probability_diabetes: float
    probability_healthy : float
    confidence          : float
    risk_level          : str
    message             : str
    model_version       : str

# ----------------------------------------------------------------
# ROUTES (API Endpoints)
# ----------------------------------------------------------------

# Route 1 — Health check
# Every production API has this
# Deployment platforms ping this to check if server is alive
@app.get("/", tags=["Health"])
def root():
    return {
        "status" : "online",
        "message": "Disease Prediction API is running",
        "docs"   : "/docs"
    }

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status"       : "healthy",
        "model_loaded" : pipeline is not None,
        "model_version": metadata['version'],
        "model_name"   : metadata['model_name']
    }

# Route 2 — Model info
@app.get("/model-info", tags=["Info"])
def model_info():
    """Returns information about the loaded model"""
    return {
        "model_name"   : metadata['model_name'],
        "version"      : metadata['version'],
        "trained_on"   : metadata['trained_on'],
        "features"     : metadata['features'],
        "performance"  : metadata['performance']
    }

# Route 3 — Main prediction endpoint
@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(patient: PatientData):
    """
    Takes patient health data and returns diabetes prediction.

    - **prediction**: 0 = No Diabetes, 1 = Diabetes
    - **probability_diabetes**: confidence score for diabetes
    - **risk_level**: LOW / MEDIUM / HIGH
    """
    try:
        # Step 1: Convert input to DataFrame
        # Pipeline expects a DataFrame with correct column names
        input_data = pd.DataFrame([{
            'Pregnancies'             : patient.Pregnancies,
            'Glucose'                 : patient.Glucose,
            'BloodPressure'           : patient.BloodPressure,
            'SkinThickness'           : patient.SkinThickness,
            'Insulin'                 : patient.Insulin,
            'BMI'                     : patient.BMI,
            'DiabetesPedigreeFunction': patient.DiabetesPedigreeFunction,
            'Age'                     : patient.Age
        }])

        # Step 2: Get prediction and probability
        prediction   = int(pipeline.predict(input_data)[0])
        # predict() returns array → [0] gets first element → int() converts numpy int to Python int

        probabilities = pipeline.predict_proba(input_data)[0]
        # predict_proba returns [[prob_class0, prob_class1]]
        # [0] gets first row → gives [prob_no_diabetes, prob_diabetes]

        prob_healthy  = round(float(probabilities[0]) * 100, 2)
        prob_diabetes = round(float(probabilities[1]) * 100, 2)
        confidence    = round(max(prob_healthy, prob_diabetes), 2)

        # Step 3: Determine risk level
        if prob_diabetes >= 70:
            risk_level = "HIGH"
            message    = "High diabetes risk detected. Please consult a doctor immediately."
        elif prob_diabetes >= 40:
            risk_level = "MEDIUM"
            message    = "Moderate diabetes risk. Consider lifestyle changes and regular checkups."
        else:
            risk_level = "LOW"
            message    = "Low diabetes risk. Maintain healthy lifestyle habits."

        # Step 4: Return structured response
        return PredictionResponse(
            prediction           = prediction,
            prediction_label     = "Diabetes Detected" if prediction == 1 else "No Diabetes",
            probability_diabetes = prob_diabetes,
            probability_healthy  = prob_healthy,
            confidence           = confidence,
            risk_level           = risk_level,
            message              = message,
            model_version        = metadata['version']
        )

    except Exception as e:
        # If anything goes wrong, return a proper HTTP error
        # Never expose raw Python errors to users in production
        raise HTTPException(
            status_code = 500,
            detail      = f"Prediction failed: {str(e)}"
        )
