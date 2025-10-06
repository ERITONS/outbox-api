from app.db.database import Base
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import mapped_column


class Inventory(Base):
    __tablename__= "inventory"

    product_id = mapped_column(ForeignKey("product.id",ondelete="CASCADE"), primary_key=True)
    total = Column(Integer, nullable=False)
    reserved = Column(Integer, nullable=False,default=0)
    available = Column(Integer, nullable=False)
 