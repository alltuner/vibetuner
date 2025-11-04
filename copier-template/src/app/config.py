from pydantic_settings import SettingsConfigDict
from vibetuner.config import CoreConfiguration, _load_project_config


class Configuration(CoreConfiguration):
    # Add here your configuration variables between this comment and the next one
    # Until here

    model_config = SettingsConfigDict(
        case_sensitive=False, extra="ignore", env_file=".env"
    )


settings = Configuration(project=_load_project_config())
