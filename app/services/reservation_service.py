from datetime import datetime, timedelta, timezone

from repositories.inventory_repository import InventoryRepository
from repositories.outbox_repository import OuboxRepository
from repositories.product_repository import ProductRespository
from repositories.reservation_repository import ReservationRepository
from sqlalchemy.orm import Session


class ReservationService:
    def __init__(self, 
                 reservation_repo: ReservationRepository, 
                 product_repo: ProductRespository,
                 inventory_repo: InventoryRepository,
                 outbox_repo: OuboxRepository
    ):
        self.reservation_repo = reservation_repo
        self.product_repo = product_repo
        self.inventory_repo = inventory_repo
        self.outbox_repo = outbox_repo

    def register_reservation(self, db: Session, reservation_data) -> dict:
        
        if reservation_data.qty <= 0:
            raise ValueError("qty must be > 0")

        product =  self.product_repo.get_by_sku(reservation_data.sku)
        if not product:
            raise ValueError("SKU not found")
        
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        user_id = getattr(reservation_data,"user_id", None)

        with db.begin():
            ok = self.inventory_repo.reserve_atomic(product_id=product.id, qty=reservation_data.qty)
            if not ok:
                raise ValueError("Insufficient inventory")
            
        reservation =  self.reservation_repo.create(
            product_id=product.id,
            qty=reservation_data.qty,
            user_id=user_id,
            expires_at=expires_at,
            status="pending",
        )

        self.outbox_repo.create_event(
            aggregate_type="reservation",
            aggregate_id=reservation.id,
            event_type="ReservationPending",
            payload={
                "reservation_id":reservation.id,
                "product_id": product.id,
                "sku": reservation_data.sku,
                "qty": reservation_data.qty,
                "user_id": user_id,
                "expires_at": expires_at.isoformat(),
            }
        )
         
        return {"reservation_id": reservation.id, "status": "pending", "expires_at": expires_at}