import warnings

import joblib  # type: ignore[import-untyped]
import numpy as np
from smolagents import Tool  # type: ignore[import-untyped]

try:
    from sklearn.exceptions import InconsistentVersionWarning # type: ignore
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
except ImportError:
    pass


class ScalingPredictorTool(Tool):
    """Wraps Project 3 GradientBoostingClassifier for scaling prediction."""

    name = "scaling_predictor"
    description = "Predicts if cloud workload needs to scale up based on metrics"
    inputs = {"metrics": {"type": "object", "description": "dict of metric name -> value"}}
    output_type = "object"

    def __init__(self, models_dir: str = "models"):
        super().__init__()
        self.classifier = joblib.load(f"{models_dir}/scaling_classifier.pkl")
        self.scaler = joblib.load(f"{models_dir}/scaling_scaler.pkl")
        self.features = joblib.load(f"{models_dir}/scaling_features.pkl")

    def forward(self, metrics: dict) -> dict:
        feature_vectors = [[metrics[x] for x in self.features]]
        scaled_vectors = self.scaler.transform(feature_vectors)
        prediction = self.classifier.predict(scaled_vectors)[0]
        proba = self.classifier.predict_proba(scaled_vectors)[0]

        return {
            "scale_up": bool(prediction),
            "confidence": float(proba[prediction]),
            "recommendation": "scale up now" if prediction else "no action"
        }
