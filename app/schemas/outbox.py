from datetime import datetime
from decimal import Decimal
from typing import Any, Dict

from pydantic import BaseModel


class OutboxCreate(BaseModel):
    id : int
    aggregate_id: int 
    aggregate_type: str
    event_type: str
    payload_json: Dict[str, Any]  
    status: str
    created_at: datetime
    published_at: datetime

class OutboxRead(BaseModel):
    id: int
    aggregate_id: str
    aggregate_type: str
    event_type: str
    payload_json: Dict[str, Any]  
    status: str
    created_at: datetime
    published_at: datetime