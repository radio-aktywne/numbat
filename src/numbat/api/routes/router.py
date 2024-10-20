from litestar import Router

from numbat.api.routes.ping.router import router as ping_router
from numbat.api.routes.prerecordings.router import router as prerecordings_router

router = Router(
    path="/",
    route_handlers=[
        ping_router,
        prerecordings_router,
    ],
)
