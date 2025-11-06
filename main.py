from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from api import help_requests, knowledge_base
from db.help_requests import get_help_requests_by_status

app = FastAPI()
app.include_router(help_requests.router, prefix="/help_requests")
app.include_router(knowledge_base.router, prefix="/knowledge_base")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse, tags=["dashboard"])
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/dashboard/help_requests", response_class=HTMLResponse, tags=["dashboard"])
def show_help_requests(request: Request):
    # list pending requests from DB
    from db.help_requests import get_help_requests_by_status
    items = get_help_requests_by_status("Pending")
    return templates.TemplateResponse("help_requests.html", {"request": request, "help_requests": items})

@app.get("/dashboard/knowledge_base", response_class=HTMLResponse, tags=["dashboard"])
def show_kb_entries(request: Request):
    from db.knowledge_base import get_kb_entries
    entries = get_kb_entries()
    return templates.TemplateResponse("knowledge_base.html", {"request": request, "entries": entries})

@app.get("/dashboard/all_requests", response_class=HTMLResponse, tags=["dashboard"])
def show_all_requests(request: Request):
    pending = get_help_requests_by_status("Pending")
    resolved = get_help_requests_by_status("Resolved")
    return templates.TemplateResponse(
        "all_requests.html",
        {
            "request": request,
            "pending": pending,
            "resolved": resolved
        }
    )