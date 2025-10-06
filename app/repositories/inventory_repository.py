from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryCreate, InventoryUpdate

class InventoryRepository:
    def __init__(self, db:Session):
        self.db = db

    
    def get_product_by_id(self, product_id: int) -> Inventory | None:
         return self.db.query(Inventory).filter(Inventory.product_id == product_id).first()

    def reserve_atomic(self, product_id: int, qty: int) -> None:
        res = self.db.execute(text("""
            UPDATE inventory
            SET reserved = reserved + :qty,
                available = available - :qty
            WHERE product_id = :pid and available >= : qty
        """), {"pid" : product_id, "qty": qty})
        return res.rowcount == 1
    
    def release_atomic(self, product_id: int, qty: int) -> None:
        res = self.db.execute(text("""
            UPDATE inventory
            SET reserved = reserved - :qty,
                available = available + :qty
            WHERE product_id = :pid
        """), {"pid" : product_id, "qty": qty})
        return res.rowcount == 1    


