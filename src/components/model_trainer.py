import sys
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from src.exception import CustomException
from src.logger import logger
from src.utils import save_object

class ModelTrainer:
    def __init__(self):
        self.model_path = "artifacts/model.pkl"

    def initiate_model_trainer(self, train_array, test_array):
        try:
            logger.info("Starting model training")

            X_train = train_array[:, :-7]
            y_train = train_array[:, -7:]

            X_test = test_array[:, :-7]
            y_test = test_array[:, -7:]

            base_model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
            model = MultiOutputRegressor(base_model)
            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred, multioutput="uniform_average")

            logger.info(f"Training complete. MAE: {mae:.4f}, R2(avg): {r2:.4f}")

            save_object(self.model_path, model)

            return {"model_path": self.model_path, "mae": float(mae), "r2": float(r2)}
        except Exception as e:
            raise CustomException(e, sys)
