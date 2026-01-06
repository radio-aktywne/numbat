from litestar import Router

from numbat.api.routes.prerecordings.controller import Controller

router = Router(
    path="/prerecordings",
    tags=["Prerecordings"],
    route_handlers=[
        Controller,
    ],
)
