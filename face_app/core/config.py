import os
from pathlib import Path
from dotenv import load_dotenv
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
env_path = Path(".") / ".env" 
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    # App
    app_name: str
    env: str = "dev"

    # Mongo
    MONGO_URI: str = os.getenv('MONGO_URI')
    MONGO_DATABASE_NAME: str = os.getenv('MONGO_DATABASE_NAME')
    MONGO_NAME: str = os.getenv('MONGO_NAME')
    MONGO_PASSWORD: str = os.getenv('MONGO_PASSWORD')

    # Face config
    face_image_size: int = 480
    face_sim_threshold: float = 0.5
    ear_threshold: float = 0.1
    FACE_IMAGE_SIZE: int = Field(default=480, description="Input image size")
    FACE_SIM_THRESHOLD: float = Field(default=0.5)
    EAR_THRESHOLD: float = Field(default=0.1)
    # JWT
    JWT_SECRET: str = os.getenv('JWT_SECRET')
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM', "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
