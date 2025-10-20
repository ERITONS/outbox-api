from fastapi import FastAPI

from app.api.reservation import router as reservation_router
from app.api.product import router as product_router
from app.api.inventory import router as inventory_router
from app.api.payments import router as payment_router  

app = FastAPI()

app.include_router(reservation_router)
app.include_router(product_router)
app.include_router(inventory_router)
app.include_router(payment_router)


@app.get("/health")
def health():
    return {"status": "ok"}





