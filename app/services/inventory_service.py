from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventory import InventoryCreate
from app.models.inventory import Inventory

class InventoryService:
    def __init__(self, inventory_repo: InventoryRepository):
        self.inventory_repo = inventory_repo

    def register_inventory(self, inventory_data: InventoryCreate) -> Inventory:
    
        return self.inventory_repo.create(inventory_data)
