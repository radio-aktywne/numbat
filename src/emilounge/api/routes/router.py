from litestar import Router

from emilounge.api.routes.ping.router import router as ping_router
from emilounge.api.routes.prerecordings.router import router as prerecordings_router

router = Router(
    path="/",
    route_handlers=[
        ping_router,
        prerecordings_router,
    ],
)
