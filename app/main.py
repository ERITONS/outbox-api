from fastapi import FastAPI

from app.api.reservation import router as reservation_router

app = FastAPI()

app.include_router(reservation_router)


@app.get("/health")
def health():
    return {"status": "ok"}





