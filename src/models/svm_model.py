import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
import json


class OnePieceFightPredictor:
    """
    ONE PIECE Fight Predictor using SVM with engineered features.

    This model predicts fight outcomes based on difference variables between fighters,
    with special handling for Conqueror's Haki interactions.
    """

    def __init__(self):
        self.model = SVC(random_state=42, probability=True)
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.is_fitted = False

        # Feature definitions based on notebook analysis
        self.base_diff_features = [
            "reaction_speed_diff",
            "stamina_diff",
            "strength_diff",
            "offense_diff",
            "defense_diff",
            "combat_skills_diff",
            "battle_iq_diff",
            "armament_haki_diff",
            "observation_haki_diff",
            "experience_diff",
        ]

        self.engineered_features = ["conqueror_present", "conqueror_impact"]
        self.all_features = self.base_diff_features + self.engineered_features

    def engineer_conqueror_features(self, df):
        """
        Engineer Conqueror's Haki interaction features.

        Args:
            df: DataFrame with fighter attributes

        Returns:
            DataFrame with engineered features added
        """
        df = df.copy()

        # Create conqueror_present: 1 if either fighter has Conqueror's Haki
        df["conqueror_present"] = (
            (df["fighter_1_conqueror_haki"] > 0) | (df["fighter_2_conqueror_haki"] > 0)
        ).astype(int)

        # Create conqueror_impact: amplified difference when relevant
        df["conqueror_impact"] = df["conqueror_haki_diff"] * df["conqueror_present"]

        return df

    def prepare_features(self, df):
        """
        Prepare features for training or prediction.

        Args:
            df: DataFrame with fight data

        Returns:
            X: Feature matrix with engineered features
        """
        # Engineer Conqueror's Haki features
        df_engineered = self.engineer_conqueror_features(df)

        # Select final feature set
        X = df_engineered[self.all_features]

        return X

    def fit(self, df, target_column="outcome"):
        """
        Train the SVM model on fight data.

        Args:
            df: DataFrame with fight data
            target_column: Name of the target column
        """
        print("Training ONE PIECE Fight Predictor...")
        print("=" * 50)

        # Prepare features
        X = self.prepare_features(df)
        y = df[target_column]

        print(f"Features: {X.shape[1]}")
        print(f"Samples: {X.shape[0]}")
        print(f"Target classes: {y.unique()}")

        # Encode target variable
        y_encoded = self.label_encoder.fit_transform(y)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )

        # Scale features (important for SVM)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        self.model.fit(X_train_scaled, y_train)

        # Evaluate on test set
        y_pred = self.model.predict(X_test_scaled)
        test_accuracy = accuracy_score(y_test, y_pred)

        print(f"\nTraining completed!")
        print(f"Test Accuracy: {test_accuracy:.4f}")
        print(f"Classes: {self.label_encoder.classes_}")

        self.is_fitted = True

        return self

    def predict(self, df):
        """
        Predict fight outcomes.

        Args:
            df: DataFrame with fight data

        Returns:
            predictions: Array of predicted outcomes
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")

        X = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)

        predictions_encoded = self.model.predict(X_scaled)
        predictions = self.label_encoder.inverse_transform(predictions_encoded)

        return predictions

    def predict_proba(self, df):
        """
        Predict fight outcome probabilities.

        Args:
            df: DataFrame with fight data

        Returns:
            probabilities: Array of prediction probabilities
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")

        X = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)

        probabilities = self.model.predict_proba(X_scaled)

        return probabilities

    def get_feature_importance(self, df):
        """
        Analyze feature correlations with the target variable.

        Args:
            df: DataFrame with fight data and target

        Returns:
            correlations: Sorted list of (feature, correlation) tuples
        """
        X = self.prepare_features(df)
        y_encoded = self.label_encoder.fit_transform(df["outcome"])

        correlations = []
        for feature in self.all_features:
            corr = np.corrcoef(X[feature], y_encoded)[0, 1]
            correlations.append((feature, abs(corr)))

        # Sort by absolute correlation
        correlations.sort(key=lambda x: x[1], reverse=True)

        return correlations

    def save_model(self, filepath):
        """
        Save the trained model and preprocessors.

        Args:
            filepath: Path to save the model
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before saving")

        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "label_encoder": self.label_encoder,
            "features": self.all_features,
        }

        os.makedirs('models', exist_ok=True)
        joblib.dump(model_data, 'models/svm_fight_predictor.pkl')
        joblib.dump(self.label_encoder, 'models/label_encoder.pkl')
        joblib.dump(self.scaler, 'models/feature_scaler.pkl')

        metadata = {
            "features": self.all_features,
            "classes": self.label_encoder.classes_.tolist(),
        }
        with open('models/model_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"Model and metadata saved to {filepath}")

    def load_model(self, filepath):
        """
        Load a trained model and preprocessors.

        Args:
            filepath: Path to the saved model
        """
        model_data = joblib.load(filepath)

        self.model = model_data["model"]
        self.scaler = model_data["scaler"]
        self.label_encoder = model_data["label_encoder"]
        self.all_features = model_data["features"]
        self.is_fitted = True

        print(f"Model loaded from {filepath}")
        return self


def main():
    """
    Example usage of the OnePieceFightPredictor
    """
    # Load data
    try:
        df = pd.read_csv("data/processed/fight_data_cleaned.csv")
        print(f"Loaded dataset: {df.shape}")
    except FileNotFoundError:
        print("Data file not found. Please ensure the cleaned data exists.")
        return

    # Initialize and train predictor
    predictor = OnePieceFightPredictor()
    predictor.fit(df)

    # Analyze feature importance
    print("\nFEATURE IMPORTANCE ANALYSIS")
    print("=" * 40)
    correlations = predictor.get_feature_importance(df)

    for i, (feature, corr) in enumerate(correlations[:10], 1):
        marker = "🔥" if "conqueror" in feature else "  "
        print(f"{i:2d}. {marker} {feature}: {corr:.3f}")

    # Save model
    predictor.save_model("../../models/one_piece_fight_predictor.pkl")

    print("\nModel training and deployment preparation complete!")


if __name__ == "__main__":
    main()
