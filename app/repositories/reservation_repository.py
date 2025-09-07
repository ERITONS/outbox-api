from models.reservation import Reservation
from sqlalchemy import text
from sqlalchemy.orm import Session


class ReservationRepository:

    def __init__(self, db:Session):
        self.db = db
    
    def create(self, *, product_id: int, qty: int, user_id: str, expires_at, status: str = "pending") -> Reservation:
        row = self.db.execute(text("""
            INSERT INTO reservation(product_id, qty, user_id, status, expires_at)
            VALUES (:pid, :qty, :uid, :st, :exp)
            RETURNING ID
        """), {"pid": product_id, "qty": qty, "uid": user_id, "st": status, "exp": expires_at}).first()
        r = Reservation(id=row.id, product_id = product_id, qty=qty, user_id=user_id, status=status, expires_at=expires_at)
        return r

    
    