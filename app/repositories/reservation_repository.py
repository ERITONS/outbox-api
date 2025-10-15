import logging
from app.models.reservation import Reservation
from sqlalchemy import text
from sqlalchemy.orm import Session


class ReservationRepository:

    def __init__(self, db:Session):
        self.db = db
    
    def create(self, *, sku: str, qty: int, user_id: str, expires_at, status: str = "pending") -> Reservation:
       
        row = self.db.execute(text("""
            INSERT INTO flashsale.reservation(sku, qty, user_id, status, expires_at)
            VALUES (:sku, :qty, :uid, :st, :exp)
            RETURNING ID, CREATE_AT
        """), {"sku": sku, "qty": qty, "uid": user_id, "st": status, "exp": expires_at}).first()
        r = Reservation(id=row.id, sku=sku, qty=qty, user_id=user_id, status=status, create_at=row.create_at, expires_at=expires_at)
        logging.info(f"Created reservation: {row}")
        return r

    
    