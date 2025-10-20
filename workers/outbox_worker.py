import json, time, pika
from sqlalchemy import text
from app.db.database import SessionLocal
from app.core.config import settings

def get_channel():
    params = pika.URLParameters(settings.RABBITMQ_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    # exchange de eventos (topic)
    ch.exchange_declare(exchange="domain.events", exchange_type="topic", durable=True)
    return conn, ch

def publish_event(ch, routing_key: str, payload: dict):
    ch.basic_publish(
        exchange="domain.events",
        routing_key=routing_key,                # ex: reservation.pending
        body=json.dumps(payload).encode(),
        properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
    )

def run():
    while True:
        with SessionLocal() as db:
            rows = db.execute(text("""
                SELECT id, event_type, payload_json
                FROM flashsale.outbox
                WHERE status='pending'
                ORDER BY id
                FOR UPDATE SKIP LOCKED
                LIMIT 100
            """)).fetchall()

            if not rows:
                time.sleep(1); continue

            conn, ch = get_channel()
            try:
                for r in rows:
                    rk = {
                        "ReservationPending": "reservation.pending",
                        "ReservationExpired": "reservation.expired",
                        "ReservationConfirmed": "reservation.confirmed",
                    }.get(r.event_type, "unknown")

                    publish_event(ch, rk, r.payload_json)
                    db.execute(text("UPDATE flashsale.outbox SET status='published', published_at=NOW() WHERE id=:id"), {"id": r.id})
                db.commit()
            except Exception:
                db.rollback()
            finally:
                ch.close(); conn.close()

if __name__ == "__main__":
    run()