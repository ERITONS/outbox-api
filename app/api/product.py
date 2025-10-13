from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.product import ProductCreate
from app.repositories import(
    product_repository as pr,
  )
from app.services.product_service import ProductService
from app.db.dependencies import get_db

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", status_code=201)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
   
    service = ProductService(
      pr.ProductRespository(db),
    )
    try:
        return service.register_product(product_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


