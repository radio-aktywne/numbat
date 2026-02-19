from litestar import Router

from numbat.api.routes.ping.router import router as ping
from numbat.api.routes.prerecordings.router import router as prerecordings
from numbat.api.routes.sse.router import router as sse
from numbat.api.routes.test.router import router as test

router = Router(
    path="/",
    route_handlers=[
        ping,
        prerecordings,
        sse,
        test,
    ],
)
