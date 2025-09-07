from models.outbox import Outbox
from repositories.outbox_repository import OuboxRepository
from schemas.outbox import OutboxCreate


class OutboxService:
    def __init__(self, outbox_repo: OuboxRepository):
        self.outbox_repo = outbox_repo

    def register_outbox(self, outbox_data: OutboxCreate) -> Outbox:
    
        return self.outbox_repo.create_event(outbox_data)