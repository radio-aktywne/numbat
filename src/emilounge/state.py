from litestar.datastructures import State as LitestarState

from emilounge.config.models import Config
from emilounge.services.emishows.service import EmishowsService
from emilounge.services.medialounge.service import MedialoungeService


class State(LitestarState):
    """Use this class as a type hint for the state of the service."""

    config: Config
    """Configuration for the service."""

    emishows: EmishowsService
    """Service for emishows service."""

    medialounge: MedialoungeService
    """Service for medialounge database."""
