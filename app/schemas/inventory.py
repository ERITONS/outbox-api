from pydantic import BaseModel
from datetime import datetime


class InventoryCreate(BaseModel):
    total: int
    reserved: int
    available: int

class InventoryRead(BaseModel):
    product_id: int
    total: int
    reserved: int
    available: int

class InventoryUpdate(BaseModel):
    product_id: int
    total: int
    reserved: int
    available: int