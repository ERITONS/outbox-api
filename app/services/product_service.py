from repositories.product_repository import ProductRespository
from schemas.product import ProductCreate
from models.product import Product

class ProductService:
    def __init__(self, product_repo: ProductRespository):
        self.product_repo = product_repo

    def register_product(self, product_data: ProductCreate) -> Product:
        existing_product = self.product_repo.get_by_id(product_data.id)
        if existing_product:
            raise ValueError("Sku already registered")
        return self.product_repo.create(product_data)
