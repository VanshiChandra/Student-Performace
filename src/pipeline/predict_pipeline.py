import pandas as pd
import numpy as np
from src.utils import load_object
import os

class PredictPipeline:
    def __init__(self):
        self.model_path = os.path.join("artifacts", "model.pkl")
        self.preprocessor_path = os.path.join("artifacts", "preprocessor.pkl")
        self.model = load_object(self.model_path)
        self.preprocessor = load_object(self.preprocessor_path)

    def predict(self, df: pd.DataFrame):
        X = df[["gender", "race_ethnicity", "parental_level_of_education",
                "lunch", "test_preparation_course"]]
        X_transformed = self.preprocessor.transform(X)
        y_pred = self.model.predict(X_transformed)
        subjects = ["math_score","reading_score","writing_score","science_score",
                    "history_score","english_score","computer_score"]
        predictions = {subj: df[subj].values[0] for subj in subjects}
        overall = np.mean(list(predictions.values()))
        strongest = max(predictions, key=predictions.get).replace("_"," ").title()
        weakest = min(predictions, key=predictions.get).replace("_"," ").title()
        return {"predictions": predictions,
                "overall_percentage": round(overall,2),
                "strongest": strongest,
                "weakest": weakest}
