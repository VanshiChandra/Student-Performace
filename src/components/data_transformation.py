import os, sys
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from src.exception import CustomException
from src.logger import logger
from src.utils import save_object

class DataTransformation:
    def __init__(self):
        self.preprocessor_path = os.path.join("artifacts", "preprocessor.pkl")

    def get_preprocessor_object(self):
        try:
            categorical_cols = [
                "gender",
                "race_ethnicity",
                "parental_level_of_education",
                "lunch",
                "test_preparation_course"
            ]
            cat_pipeline = Pipeline([
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
            ])
            preprocessor = ColumnTransformer(transformers=[
                ("cat", cat_pipeline, categorical_cols)
            ], remainder="drop")
            return preprocessor
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_transformation(self, train_path, test_path):
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)

            logger.info("Preparing data for transformation")

            target_cols = [
                "math_score",
                "reading_score",
                "writing_score",
                "science_score",
                "social_score",
                "english_score",
                "computer_score"
            ]
            feature_cols = [
                "gender",
                "race_ethnicity",
                "parental_level_of_education",
                "lunch",
                "test_preparation_course"
            ]

            X_train = train_df[feature_cols]
            y_train = train_df[target_cols]
            X_test = test_df[feature_cols]
            y_test = test_df[target_cols]

            preprocessor = self.get_preprocessor_object()

            logger.info("Fitting preprocessor on training features")
            X_train_transformed = preprocessor.fit_transform(X_train)
            X_test_transformed = preprocessor.transform(X_test)

            train_array = np.c_[X_train_transformed, y_train.values]
            test_array = np.c_[X_test_transformed, y_test.values]

            save_object(self.preprocessor_path, preprocessor)

            logger.info("Data transformation complete")
            return train_array, test_array, self.preprocessor_path
        except Exception as e:
            raise CustomException(e, sys)
