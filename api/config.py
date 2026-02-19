"""
Configuration settings for the FastAPI application
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, Union
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    app_name: str = "TuniTech Advisor API"
    app_version: str = "0.1.0"
    app_description: str = "Smart Phone Recommendation System for Tunisian E-commerce"
    debug: bool = True
    
    # CORS Settings
    cors_origins: Union[str, list] = [
        "http://localhost:3000",  # React default
        "http://localhost:8000",  # FastAPI default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # API Settings
    api_prefix: str = "/api/v1"
    
    # MLflow Settings
    mlflow_tracking_uri: str = "./mlruns"
    mlflow_experiment_name: str = "smartphone-price-prediction"
    
    # Model Settings
    model_path: Optional[str] = None  # Will be loaded from MLflow
    default_model_name: str = "best_model"
    
    # Data Settings
    data_path: str = "./dataset"
    unified_data_file: str = "unified_smartphones_filled.csv"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()
