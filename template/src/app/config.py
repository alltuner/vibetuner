from pydantic_settings import SettingsConfigDict

from core.config import CoreConfiguration, _load_project_config


class Configuration(CoreConfiguration):
    # Add here your configuration variables between this comment and the next one

    model_config = SettingsConfigDict(
        case_sensitive=False, extra="ignore", env_file=".env"
    )


settings = Configuration(project=_load_project_config())
