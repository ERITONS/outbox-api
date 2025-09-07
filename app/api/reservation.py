from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import SessionLocal
from schemas.reservation import ReservationCreate
from repositories import(
    reservation_repository as rr,
    product_repository as pr,
    inventory_repository as ir,
    outbox_repository as orp
)
from services.reservation_service import ReservationService
from db.dependencies import get_db

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.post("/", status_code=201)
def create_reservation(reservation_data: ReservationCreate, db: Session = Depends(get_db)):
   
    service = ReservationService(
      rr.ReservationRepository(db),
      pr.ProductRespository(db),
      ir.InventoryRepository(db),
      orp.OuboxRepository(db)
    )
    try:
        return service.register_reservation(db,reservation_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


