from fastapi import APIRouter, Request
from pydantic import BaseModel
from collections import defaultdict

site_analytics_router = APIRouter(
    prefix="/site_analytics",
    tags=["Site Analytics"],
)

visit_data = defaultdict(int)
ip_data = defaultdict(lambda: defaultdict(int))

class VisitEvent(BaseModel):
    path: str

@site_analytics_router.post("/track-visit")
async def track_visit(request: Request, visit: VisitEvent):
    client_ip = request.client.host
    print(f"Tracking visit: {visit.path} from {client_ip}")
    visit_data[visit.path] += 1
    ip_data[visit.path][client_ip] += 1
    return {"status": "tracked"}



@site_analytics_router.get("/analytics")
async def get_analytics():
    return {
        "total_visits": dict(visit_data),
        "ip_data": {path: dict(ips) for path, ips in ip_data.items()}
    }
