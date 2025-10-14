from fastapi import APIRouter
import json, pika
from core.config import settings

router = APIRouter(prefix="/payments", tags=["payments"])

def publish_payment_approved(reservation_id: int):
    params = pika.URLParameters(settings.RABBITMQ_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.exchange_declare(exchange="domain.events", exchange_type="topic", durable=True)

    payload = {"reservation_id": reservation_id}
    ch.basic_publish(
        exchange="domain.events",
        routing_key="payment.approved",
        body=json.dumps(payload).encode(),
        properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
    )
    conn.close()

@router.post("/{reservation_id}/approve")
def approve(reservation_id: int):
    publish_payment_approved(reservation_id)
    return {"status": "queued", "event": "payment.approved", "reservation_id": reservation_id}
