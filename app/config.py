from typing import Any

from dotenv import find_dotenv
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from app.api.utils.enums.env_enum import EnvEnum
from app.api.utils.enums.log_level_enum import LogLevelEnum


class CommonSettings(BaseModel):
    project_name: str = 'remnawave-gateway'
    environment: EnvEnum
    log_level: LogLevelEnum = LogLevelEnum.INFO
    human_readable_logs: bool = False
    disabled_log_endpoint: list[str] = [
        '/health',
        '/liveness',
        '/metrics',
        '/openapi.json',
        '/docs',
    ]
    logger_body_content_max_size: int = 2500
    backend_cors_origins: Any = []

    prometheus_enabled: bool = True
    struct_log: bool = True


class SwaggerSettings(BaseModel):
    doc_login: str = 'admin'
    doc_password: str = 'admin'


class AuthSettings(BaseModel):
    api_key: str


class RemnawaveSettings(BaseModel):
    """Настройки клиента Remnawave API."""

    base_url: str = 'http://localhost:3000'
    api_key: str = ''
    request_timeout: int = 20


class KafkaSettings(BaseModel):
    bootstrap_servers: str = 'localhost:9092'
    common_topic: str = 'remnawave-gateway'


class Settings(BaseSettings):
    def __init__(self, **values: Any) -> None:
        load_dotenv(find_dotenv())
        super().__init__(**values)

    model_config = SettingsConfigDict(
        env_nested_delimiter='__',
        env_file='.env',
        env_file_encoding='UTF-8',
        arbitrary_types_allowed=True,
    )

    common: CommonSettings
    swagger: SwaggerSettings = SwaggerSettings()
    auth: AuthSettings
    remnawave: RemnawaveSettings = RemnawaveSettings()
    kafka: KafkaSettings = KafkaSettings()


config = Settings()
