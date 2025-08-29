from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer
from src.logger import logger

def run_training():
    logger.info("Training pipeline started")
    ingestion = DataIngestion()
    train_path, test_path = ingestion.initiate_data_ingestion()

    transformer = DataTransformation()
    train_array, test_array, preprocessor_path = transformer.initiate_data_transformation(train_path, test_path)

    trainer = ModelTrainer()
    metrics = trainer.initiate_model_trainer(train_array, test_array)

    logger.info(f"Training finished. Metrics: {metrics}")

if __name__ == "__main__":
    run_training()
