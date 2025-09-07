from pydantic import BaseModel
from datetime import datetime


class ReservationCreate(BaseModel):
    sku: str
    qty: int
    user_id: int
    status: str
    expires_at: datetime
    create_at: datetime

class ReservationRead(BaseModel):
    id: int
    sku: str
    qty: int
    user_id: int
    status: str
    expires_at: datetime
    create_at: datetime