import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from src.exception import CustomException
from src.logger import logger

class DataIngestion:
    def __init__(self, raw_data_path=None):
        if raw_data_path is None:
            self.raw_data_path = os.path.join("notebook", "data", "StudentsPerformance.csv")
        else:
            self.raw_data_path = raw_data_path

        self.train_path = os.path.join("artifacts", "train.csv")
        self.test_path = os.path.join("artifacts", "test.csv")

    def initiate_data_ingestion(self):
        try:
            logger.info(f"Reading dataset from: {self.raw_data_path}")
            df = pd.read_csv(self.raw_data_path)

            os.makedirs("artifacts", exist_ok=True)
            df.to_csv(os.path.join("artifacts", "raw.csv"), index=False)

            train_set, test_set = train_test_split(df, test_size=0.2, random_state=42)

            train_set.to_csv(self.train_path, index=False)
            test_set.to_csv(self.test_path, index=False)

            logger.info("Data ingestion completed.")
            return self.train_path, self.test_path
        except Exception as e:
            raise CustomException(e, sys)
