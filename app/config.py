import os


class Config:
    """Configuration class for the BJJ AI Agents app"""

    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))

    # Database Configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "bjj_app.db")

    # App Configuration
    GRADIO_SERVER_NAME: str = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    GRADIO_SERVER_PORT: int = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

    # Prompt Configuration
    PROMPTS_DIR: str = "prompts"

    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        if not cls.OPENAI_API_KEY:
            print(
                "Warning: OPENAI_API_KEY not set. Please set this environment variable."
            )
            return False
        return True

    @classmethod
    def get_openai_config(cls) -> dict:
        """Get OpenAI configuration as a dictionary"""
        return {
            "model": cls.OPENAI_MODEL,
            "temperature": cls.OPENAI_TEMPERATURE,
            "max_tokens": cls.OPENAI_MAX_TOKENS,
        }
