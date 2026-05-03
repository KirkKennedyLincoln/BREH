import os
import joblib
import numpy

from smolagents import Tool


class ScalingPredictorTool(Tool):
    """Wraps Project 3 GradientBoostingClassifier for scaling prediction."""

    name = "scaling_predictor"
    description = "Predicts if cloud workload needs to scale up based on metrics"

    # TODO: Define inputs dict with "metrics" key (type: object)
    # TODO: Define output_type = "object"
    inputs = {}
    output_type = "object"

    def __init__(self, models_dir: str = None):
        super().__init__()
        self.classfier = joblib.load(f"{models_dir}/scaling_classifier.pkl")
        self.scaler = joblib.load(f"{models_dir}/scaling_scaler.pkl")
        self.features = joblib.load(f"{models_dir}/scaling_features.pkl")

    def forward(self, metrics: dict) -> dict:
        feature_vectors = [metrics[x] for x in self.features] 
        # TODO: Extract features in order from self.feature_names
        # TODO: Scale with self.scaler.transform()
        # TODO: Predict with self.model.predict() and predict_proba()
        # TODO: Return dict with scale_up (bool), confidence (float), recommendation (str)
        pass
