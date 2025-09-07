from pydantic import BaseModel
from decimal import Decimal
from typing import List 

class ProductCreate(BaseModel):    
    sku: str
    name: str
    description: str
    price: Decimal 

class ProductRead(BaseModel):
    id: int
    sku: str
    name: str
    description: str
    price: Decimal 

    class Config:
         orm_mode = True

class ProductUpdate(ProductRead):
    sku: str
    name: str
    description: str
    price: Decimal 

class ProductList(BaseModel):
    user: List[ProductRead]
