from sqlalchemy.orm import Session
from models.product import Product
from schemas.product import ProductCreate

class ProductRespository:

    def __init__(self, db:Session):
        self.db = db

    def get_by_sku(self, sku: int) -> Product | None:
        return self.db.query(Product).filter(Product.sku == sku).first()
    
    def create(self, product_data: ProductCreate) -> Product:
        product = Product(**product_data.model_dump())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
