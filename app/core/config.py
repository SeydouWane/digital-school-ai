from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # --- CONFIGURATION PROJET ---
    PROJECT_NAME: str = "Digital School AI Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # --- CLEFS API LLM ---
    GROQ_API_KEY: str = ""
    # OpenAI reste disponible pour d'autres tâches si nécessaire
    OPENAI_API_KEY: Optional[str] = ""
    
    # --- CONFIGURATION AWS (Polly & S3) ---
    
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET_AUDIO: str = "digital-school-audio-assets"
    
    # --- BASE DE DONNÉES ---
    # URL de connexion PostgreSQL (AWS RDS)
    DATABASE_URL: str = ""


    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" 
    )

settings = Settings()