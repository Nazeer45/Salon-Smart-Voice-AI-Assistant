from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from models.api import KnowledgeBaseEntry
from db.knowledge_base import add_kb_entry, get_kb_entries, delete_kb_entry

router = APIRouter()

@router.post("/", response_model=KnowledgeBaseEntry, tags=["knowledge_base"])
def create_kb_entry(data: KnowledgeBaseEntry):
    item = add_kb_entry(data.question, data.answer)
    return item

@router.get("/", response_model=list[KnowledgeBaseEntry], tags=["knowledge_base"])
def list_kb_entries():
    return get_kb_entries()

@router.post("/delete/{entry_id}", tags=["knowledge_base"])
def delete_kb_entry_api(entry_id: str, request: Request):
    delete_kb_entry(entry_id)
    return RedirectResponse(url="/dashboard/knowledge_base", status_code=303)