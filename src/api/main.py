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
    allow_origins=[
        "http://localhost:8501",  # Local Streamlit development
        "https://one-piece-match-predictors.streamlit.app/",  # Replace with your actual URL
        "https://*.streamlit.app",  # Allow any Streamlit Cloud app (optional)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models at startup
MODEL_DIR = "src/models"
MODEL_AVAILABLE = False
svm_model = scaler = label_encoder = None

try:
    # Try different possible paths
    possible_paths = [
        os.path.join(MODEL_DIR, "svm_fight_predictor.pkl"),
        os.path.join(".", MODEL_DIR, "svm_fight_predictor.pkl"),
        "svm_fight_predictor.pkl",  # If moved to root
    ]

    model_data = None
    for path in possible_paths:
        if os.path.exists(path):
            model_data = joblib.load(path)
            print(f"✅ Models loaded successfully from {path}")
            break

    if model_data:
        svm_model = model_data["model"]
        scaler = model_data["scaler"]
        label_encoder = model_data["label_encoder"]
        MODEL_AVAILABLE = True
    else:
        print("⚠️ Model files not found, using fallback prediction")

except Exception as e:
    print(f"❌ Error loading models: {e}")
    print("⚠️ Using fallback prediction method")


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

    try:
        if MODEL_AVAILABLE and svm_model is not None:
            # Use your ML model
            features = calculate_features(request.fighter_1, request.fighter_2)
            features_scaled = scaler.transform(features)
            prediction_encoded = svm_model.predict(features_scaled)[0]
            prediction = label_encoder.inverse_transform([prediction_encoded])[0]
            probabilities = svm_model.predict_proba(features_scaled)[0]
            prob_dict = {
                label: float(prob)
                for label, prob in zip(label_encoder.classes_, probabilities)
            }
            confidence = float(max(probabilities))
        else:
            # Fallback: Simple stats-based prediction
            f1_stats = request.fighter_1.model_dump()
            f2_stats = request.fighter_2.model_dump()

            f1_total = sum(f1_stats.values())
            f2_total = sum(f2_stats.values())

            if f1_total > f2_total:
                prediction = "victory"
                confidence = min(0.95, 0.5 + abs(f1_total - f2_total) / 1000)
            elif f2_total > f1_total:
                prediction = "loss"
                confidence = min(0.95, 0.5 + abs(f2_total - f1_total) / 1000)
            else:
                prediction = "draw"
                confidence = 0.5

            prob_dict = {
                "victory": confidence if prediction == "victory" else 1 - confidence,
                "loss": confidence if prediction == "loss" else 1 - confidence,
                "draw": confidence if prediction == "draw" else 0.1,
            }

        # Calculate fighter advantages
        f1_stats = request.fighter_1.model_dump()
        f2_stats = request.fighter_2.model_dump()
        advantages = {
            stat: round(f1_stats[stat] - f2_stats[stat], 2) for stat in f1_stats.keys()
        }

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
