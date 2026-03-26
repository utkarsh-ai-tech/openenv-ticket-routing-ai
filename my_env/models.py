from pydantic import BaseModel
from typing import Optional

class Action(BaseModel):
    category: str
    priority: str
    response: str
    escalate: bool

class Observation(BaseModel):
    ticket_id: int
    message: str
    history: Optional[str] = None