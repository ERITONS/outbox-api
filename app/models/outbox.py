from sqlalchemy import Column, Integer, String, JSON, DateTime
from app.db.database import Base

class Outbox(Base):
    __tablename__= "outbox"

    id = Column(Integer, primary_key=True, index=True)
    aggregate_type = Column(String,nullable=False)
    aggregate_id = Column(String,nullable=False)
    event_type = Column(String,nullable=False)
    payload_json = Column(JSON,nullable=False)
    status = Column(String,nullable=False)
    created_at = Column(DateTime(timezone=True),nullable=False)
    published_at = Column(DateTime(timezone=True),nullable=False)