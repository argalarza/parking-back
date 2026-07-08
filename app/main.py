from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from app.modules.access.adapters.inbound.http.router import router as access_router
from app.modules.admin_users.adapters.inbound.http.router import router as admin_users_router
from app.modules.auth.adapters.inbound.http.router import router as auth_router
from app.modules.gates.adapters.inbound.http.router import router as gates_router
from app.modules.guests.adapters.inbound.http.router import router as guests_router
from app.modules.persons.adapters.inbound.http.router import router as persons_router
from app.modules.subscriptions.adapters.inbound.http.router import router as subscriptions_router
from app.modules.vehicles.adapters.inbound.http.router import router as vehicles_router


app = FastAPI(title="UPark Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_origin_regex=r"^http://(127\.0\.0\.1|localhost):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["default"])
def raiz() -> dict:
    return {"mensaje": "El backend del parqueadero esta funcionando"}


def include_router_compat(router: APIRouter) -> None:
    # FastAPI in this environment registers included routers as placeholders,
    # so we append the concrete APIRoutes to keep route discovery stable.
    before_route_ids = {id(route) for route in app.router.routes}
    app.include_router(router)

    added_routes = [
        route
        for route in app.router.routes
        if id(route) not in before_route_ids and isinstance(route, APIRoute)
    ]
    if added_routes:
        return

    for route in router.routes:
        if isinstance(route, APIRoute):
            app.router.routes.append(route)


include_router_compat(persons_router)
include_router_compat(vehicles_router)
include_router_compat(access_router)
include_router_compat(auth_router)
include_router_compat(admin_users_router)
include_router_compat(gates_router)
include_router_compat(guests_router)
include_router_compat(subscriptions_router)
