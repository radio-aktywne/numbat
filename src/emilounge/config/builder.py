from pydantic import ValidationError

from emilounge.config.errors import ConfigError
from emilounge.config.models import Config


class ConfigBuilder:
    """Builds the config."""

    def build(self) -> Config:
        """Build the config."""

        try:
            return Config()
        except ValidationError as ex:
            raise ConfigError from ex
