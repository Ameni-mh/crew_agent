from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="forbid",
        case_sensitive=False,
    )

    # OpenAI API key
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    agentops_api_key: str = Field( alias="AGENTOPS_API_KEY")

    # Redis configuration
    redis_host: str = Field(alias="REDIS_HOST")
    redis_port: int = Field(alias="REDIS_PORT")
    REDIS_PASSWORD: str = Field(alias="REDIS_PASSWORD")
    redis_url: str = Field(alias="REDIS_URL")

    # GDS (Global Distribution System) API
    gds_api_key: str = Field(alias="GDS_API_KEY")
    gds_base_url: str = Field(alias="GDS_BASE_URL")
    
    

    

# ✅ Export a singleton instance
settings = Settings()
