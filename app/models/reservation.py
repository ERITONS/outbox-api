from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class Reservation(Base):
    __tablename__= "reservation"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, nullable=False)
    qty = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True))
    create_at = Column(DateTime(timezone=True), server_default=func.now())
