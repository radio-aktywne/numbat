from litestar.datastructures import State as LitestarState

from numbat.config.models import Config
from numbat.services.amber.service import AmberService
from numbat.services.beaver.service import BeaverService


class State(LitestarState):
    """Use this class as a type hint for the state of the service."""

    amber: AmberService
    """Service for amber database."""

    beaver: BeaverService
    """Service for beaver service."""

    config: Config
    """Configuration for the service."""
