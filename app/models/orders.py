from sqlalchemy import Column, Integer, String, Numeric
from db.database import Base

class Order(Base):
    __tablename__= "orders"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, nullable=False)
    name = Column(String,nullable=False)
    description = Column(String,nullable=False)
    price = Column(Numeric(10,2), nullable=False)
