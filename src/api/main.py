from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import numpy as np
import pandas as pd
import os
from typing import Dict, List

# Initialize FastAPI app
app = FastAPI(
    title="One Piece Fight Predictor API",
    description="Predict fight outcomes between One Piece characters using ML",
    version="1.0.0",
)

# Add CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with Streamlit app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models at startup
MODEL_DIR = "src/models"
try:
    # Load the dictionary containing all components
    model_data = joblib.load(os.path.join(MODEL_DIR, "svm_fight_predictor.pkl"))
    svm_model = model_data["model"]  # Extract the actual SVM model
    scaler = model_data["scaler"]  # Extract the scaler
    label_encoder = model_data["label_encoder"]  # Extract the label encoder

    print("✅ Models loaded successfully")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    svm_model = label_encoder = scaler = None


# Request/Response models
class FighterStats(BaseModel):
    reaction_speed: float = Field(
        ..., ge=0, le=100, description="Reaction speed (0-100)"
    )
    stamina: float = Field(..., ge=0, le=100, description="Stamina (0-100)")
    strength: float = Field(..., ge=0, le=100, description="Strength (0-100)")
    offense: float = Field(..., ge=0, le=100, description="Offense (0-100)")
    defense: float = Field(..., ge=0, le=100, description="Defense (0-100)")
    combat_skills: float = Field(..., ge=0, le=100, description="Combat skills (0-100)")
    battle_iq: float = Field(..., ge=0, le=100, description="Battle IQ (0-100)")
    armament_haki: float = Field(..., ge=0, le=100, description="Armament Haki (0-100)")
    observation_haki: float = Field(
        ..., ge=0, le=100, description="Observation Haki (0-100)"
    )
    conqueror_haki: float = Field(
        ..., ge=0, le=100, description="Conqueror's Haki (0-100)"
    )
    experience: float = Field(..., ge=0, le=100, description="Experience (0-100)")


class FightPredictionRequest(BaseModel):
    fighter_1: FighterStats
    fighter_2: FighterStats


class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    fighter_1_advantage: Dict[str, float]
    summary: str


# Health check endpoint
@app.get("/health")
async def health_check():
    model_status = "loaded" if svm_model is not None else "not_loaded"
    return {"status": "healthy", "model_status": model_status, "version": "1.0.0"}


# Model info endpoint
@app.get("/model/info")
async def model_info():
    if svm_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {
        "model_type": "Support Vector Machine",
        "features": 12,
        "classes": label_encoder.classes_.tolist(),
        "accuracy": "96.26%",
        "feature_engineering": "Difference variables + Conqueror's Haki interaction",
    }


def calculate_features(fighter_1: FighterStats, fighter_2: FighterStats) -> np.ndarray:
    """Calculate the 12 engineered features from fighter stats."""

    # Convert to dictionaries
    f1_dict = fighter_1.model_dump()
    f2_dict = fighter_2.model_dump()

    # Calculate base difference features (10 features)
    base_features = [
        f1_dict["reaction_speed"] - f2_dict["reaction_speed"],
        f1_dict["stamina"] - f2_dict["stamina"],
        f1_dict["strength"] - f2_dict["strength"],
        f1_dict["offense"] - f2_dict["offense"],
        f1_dict["defense"] - f2_dict["defense"],
        f1_dict["combat_skills"] - f2_dict["combat_skills"],
        f1_dict["battle_iq"] - f2_dict["battle_iq"],
        f1_dict["armament_haki"] - f2_dict["armament_haki"],
        f1_dict["observation_haki"] - f2_dict["observation_haki"],
        f1_dict["experience"] - f2_dict["experience"],
    ]

    # Calculate Conqueror's Haki features (2 features)
    conqueror_present = (
        1 if (f1_dict["conqueror_haki"] > 0 or f2_dict["conqueror_haki"] > 0) else 0
    )
    conqueror_diff = f1_dict["conqueror_haki"] - f2_dict["conqueror_haki"]
    conqueror_impact = conqueror_diff * conqueror_present

    # Combine all features
    features = base_features + [conqueror_present, conqueror_impact]

    return np.array(features).reshape(1, -1)


@app.post("/predict", response_model=PredictionResponse)
async def predict_fight(request: FightPredictionRequest):
    """Predict the outcome of a fight between two characters."""

    if svm_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Calculate features
        features = calculate_features(request.fighter_1, request.fighter_2)

        # Scale features
        features_scaled = scaler.transform(features)

        # Make prediction
        prediction_encoded = svm_model.predict(features_scaled)[0]
        prediction = label_encoder.inverse_transform([prediction_encoded])[0]

        # Get probabilities
        probabilities = svm_model.predict_proba(features_scaled)[0]
        prob_dict = {
            label: float(prob)
            for label, prob in zip(label_encoder.classes_, probabilities)
        }

        # Calculate confidence (max probability)
        confidence = float(max(probabilities))

        # Calculate fighter advantages
        f1_stats = request.fighter_1.model_dump()
        f2_stats = request.fighter_2.model_dump()
        advantages = {}

        for stat in f1_stats.keys():
            diff = f1_stats[stat] - f2_stats[stat]
            advantages[stat] = round(diff, 2)

        # Generate summary
        if prediction == "victory":
            summary = f"Fighter 1 wins with {confidence:.1%} confidence"
        elif prediction == "loss":
            summary = f"Fighter 2 wins with {confidence:.1%} confidence"
        else:
            summary = f"Draw predicted with {confidence:.1%} confidence"

        return PredictionResponse(
            prediction=prediction,
            confidence=confidence,
            probabilities=prob_dict,
            fighter_1_advantage=advantages,
            summary=summary,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


# Example endpoint
@app.get("/example")
async def get_example():
    """Get an example request for testing."""
    return {
        "fighter_1": {
            "reaction_speed": 85,
            "stamina": 90,
            "strength": 95,
            "offense": 88,
            "defense": 82,
            "combat_skills": 92,
            "battle_iq": 85,
            "armament_haki": 80,
            "observation_haki": 75,
            "conqueror_haki": 90,
            "experience": 88,
        },
        "fighter_2": {
            "reaction_speed": 78,
            "stamina": 85,
            "strength": 82,
            "offense": 80,
            "defense": 88,
            "combat_skills": 85,
            "battle_iq": 90,
            "armament_haki": 85,
            "observation_haki": 88,
            "conqueror_haki": 0,
            "experience": 85,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
