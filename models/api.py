from typing import Optional
from pydantic import BaseModel

class HelpRequestCreate(BaseModel):
    customer_id: str
    question: str

class HelpRequest(BaseModel):
    id: str
    customer_id: str
    question: str
    status: str
    created_at: str
    resolved_at: Optional[str] = None
    supervisor_answer: Optional[str] = None

class SupervisorAnswerPayload(BaseModel):
    answer: str

class KnowledgeBaseEntry(BaseModel):
    id: str
    question: str
    answer: str
    updated_at: str