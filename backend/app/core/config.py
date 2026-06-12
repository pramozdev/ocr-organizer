from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "OCR Organizer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    MAX_FILE_SIZE_MB: int = 20
    ALLOWED_EXTENSIONS: set[str] = {"png", "jpg", "jpeg", "webp"}
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    LOG_DIR: str = "logs"
    OCR_LANG: str = "por"
    OCR_USE_GPU: bool = False
    PREPROCESS_DEFAULT_GRAYSCALE: bool = True
    PREPROCESS_DEFAULT_THRESHOLD: bool = False
    PREPROCESS_DEFAULT_DENOISE: bool = True
    PREPROCESS_DEFAULT_SHARPEN: bool = True
    PREPROCESS_DEFAULT_RESIZE: bool = True
    PREPROCESS_DEFAULT_DESKEW: bool = True
    PREPROCESS_MAX_DIM: int = 2000

    model_config = ConfigDict(env_file=".env", case_sensitive=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
