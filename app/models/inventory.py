from db.database import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import mapped_column


class Inventory(Base):
    __tablename__= "inventory"

    product_id = mapped_column(ForeignKey("product.id"))
    total = Column(int, nullable=False)
    reserved = Column(int,nullable=False,default=0)
    available = Column(int,nullable=False)
 