from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.inventory import InventoryCreate
from app.repositories import(
    inventory_repository as ir,
  )
from app.services.inventory_service import InventoryService
from app.db.dependencies import get_db

router = APIRouter(prefix="/inventories", tags=["inventories"])


@router.post("/", status_code=201)
def create_inventory(inventory_data: InventoryCreate, db: Session = Depends(get_db)):
   
    service = InventoryService(
    ir.InventoryRepository(db),
    )
    try:
        return service.register_inventory(inventory_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


