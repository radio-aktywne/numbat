from litestar import Router

from emilounge.api.routes.prerecordings.controller import Controller

router = Router(
    path="/prerecordings",
    route_handlers=[
        Controller,
    ],
)
