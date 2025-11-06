from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
from models.api import HelpRequestCreate,  HelpRequest
from db.help_requests import (
    save_help_request,
    get_help_requests_by_status,
    resolve_help_request
)

router = APIRouter()

@router.post("/", response_model=HelpRequest, tags=["help_requests"])
def create_help_request(data: HelpRequestCreate):
    item = save_help_request(data.customer_id, data.question)
    return item

@router.get("/", response_model=list[HelpRequest], tags=["help_requests"])
def list_help_requests(status: str = "Pending"):
    items = get_help_requests_by_status(status)
    return items

@router.post("/{id}/resolve", tags=["help_requests"])
def resolve_request(id: str, answer: str = Form(...)):
    resolve_help_request(id, answer)
    return RedirectResponse(url="/dashboard/help_requests", status_code=303)
