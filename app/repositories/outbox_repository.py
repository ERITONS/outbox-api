from sqlalchemy.orm import Session
from sqlalchemy import text
import json

class OuboxRepository:
    def __init__(self, db:Session):
        self.db = db

    def create_event(self, *, aggregate_type: str, aggregate_id: int, event_type: str, payload: dict ) -> None:
        self.db.execute(text("""
            INSERT INTO outbox_event( aggregate_type, aggregate_id, event_type, payload_json, status)
            VALUES (:t, :id, :e, :p::jsonb, 'pending')
        """), {"t": aggregate_type, "id": aggregate_id, "e": event_type, "p": json.dumps(payload)})
        


