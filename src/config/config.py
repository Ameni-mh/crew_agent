from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="forbid",
        case_sensitive=False,
    )

    # Environment
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    agentops_api_key: int = Field( alias="AGENTOPS_API_KEY")
    

    

# ✅ Export a singleton instance
settings = Settings()
