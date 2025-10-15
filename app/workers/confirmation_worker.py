import json, pika
from sqlalchemy import text
from db.database import SessionLocal
from core.config import settings

def handle_confirm(msg: dict):
    rid = msg["reservation_id"]
    with SessionLocal() as db, db.begin():
        # pega dados da reserva
        row = db.execute(text("""
            SELECT r.id, r.product_id, r.qty, r.status FROM reservation r WHERE r.id=:rid FOR UPDATE
        """), {"rid": rid}).first()
        if not row or row.status != "pending":
            return  # idempotência básica

        # atualiza status para confirmed
        db.execute(text("UPDATE reservation SET status='confirmed' WHERE id=:rid"), {"rid": rid})

        # ajusta estoque: reservado volta a diminuir (finalizou a compra)
        db.execute(text("""
            UPDATE inventory SET reserved = GREATEST(reserved - :qty, 0)
            WHERE product_id = :pid
        """), {"qty": row.qty, "pid": row.product_id})

        # (opcional) inserir outbox_event 'ReservationConfirmed'
        db.execute(text("""
            INSERT INTO outbox_event (aggregate_type, aggregate_id, event_type, payload_json, status)
            VALUES ('reservation', :rid, 'ReservationConfirmed', :payload::jsonb, 'pending')
        """), {"rid": rid, "payload": json.dumps({"reservation_id": rid})})

def run():
    params = pika.URLParameters(settings.RABBITMQ_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.exchange_declare(exchange="domain.events", exchange_type="topic", durable=True)

    # fila específica para confirmações (pode vir de payment service)
    ch.queue_declare(queue="reservation.confirm", durable=True)
    ch.queue_bind(queue="reservation.confirm", exchange="domain.events", routing_key="reservation.confirm")

    def cb(chx, method, props, body):
        try:
            handle_confirm(json.loads(body.decode()))
            chx.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            chx.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    ch.basic_qos(prefetch_count=50)
    ch.basic_consume(queue="reservation.confirm", on_message_callback=cb)
    ch.start_consuming()

if __name__ == "__main__":
    run()