from dotenv import load_dotenv
import os
from enum import Enum

# Load environment variables from .env file
load_dotenv()

class ModelType(Enum):
    GROQ = "groq"
    OPENAI = "openai"
    CLAUDE = "claude"

class Config:
    # FastAPI settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8002"))

    # Selected model for general use
    SELECTED_MODEL: ModelType = ModelType(os.getenv("SELECTED_MODEL", ModelType.GROQ.value))

    # Image processing model
    IMAGE_PROCESSING_MODEL: ModelType = ModelType.OPENAI

    # API keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY")

    # Model-specific settings
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OPENAI_MODEL: str = "gpt-4o"
    CLAUDE_MODEL: str = "claude-2"
    OPENAI_IMAGE_MODEL: str = "gpt-4o-mini"

    @classmethod
    def get_api_key(cls, model_type: ModelType = None) -> str:
        if model_type is None:
            model_type = cls.SELECTED_MODEL

        if model_type == ModelType.GROQ:
            return cls.GROQ_API_KEY
        elif model_type == ModelType.OPENAI:
            return cls.OPENAI_API_KEY
        elif model_type == ModelType.CLAUDE:
            return cls.CLAUDE_API_KEY
        else:
            raise ValueError(f"Invalid model selected: {model_type}")

    @classmethod
    def get_model_name(cls, model_type: ModelType = None) -> str:
        if model_type is None:
            model_type = cls.SELECTED_MODEL

        if model_type == ModelType.GROQ:
            return cls.GROQ_MODEL
        elif model_type == ModelType.OPENAI:
            return cls.OPENAI_MODEL
        elif model_type == ModelType.CLAUDE:
            return cls.CLAUDE_MODEL
        else:
            raise ValueError(f"Invalid model selected: {model_type}")

    @classmethod
    def get_image_processing_model(cls) -> str:
        return cls.OPENAI_IMAGE_MODEL