from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text, bindparam
from sqlalchemy.dialects.postgresql import JSONB

class OuboxRepository:
    def __init__(self, db:Session):
        self.db = db

    def create_event(self, *, aggregate_type: str, aggregate_id: int, event_type: str, payload: dict, created_at) -> None:
        stmt = text("""
            INSERT INTO flashsale.outbox
                (aggregate_type, aggregate_id, event_type, payload_json, status, created_at, published_at)
            VALUES
                (:t, :id, :e, :p, 'pending', :ca, :pa)
            RETURNING id
        """).bindparams(
            bindparam("t"),
            bindparam("id"),
            bindparam("e"),
            bindparam("p", type_=JSONB),
            bindparam("ca"),
            bindparam("pa"),
               
        )

        row = self.db.execute(stmt, {
            "t": aggregate_type,
            "id": aggregate_id,
            "e": event_type,
            "p": payload,
            'ca': created_at,
            'pa': datetime.now(timezone.utc),               
        }).first()

        return row.id
            


