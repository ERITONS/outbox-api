from datetime import datetime, timezone
import json, pika, logging
from sqlalchemy import text, bindparam
from app.db.database import SessionLocal
from app.core.config import settings
from sqlalchemy.dialects.postgresql import JSONB


logging.basicConfig(level=logging.INFO, format="%(asctime)s [confirmation] %(levelname)s: %(message)s")

EXCHANGE = "domain.events"
QUEUE    = "payment.approved"     # <- igual ao routing key publicado pela API
ROUTING  = "payment.approved"

def handle_confirm(msg: dict):
    rid = msg["reservation_id"]
    logging.info(f"confirming reservation id={rid}")
    
    try:
        with SessionLocal() as db, db.begin():
            # pega dados da reserva
            row = db.execute(text("""
                SELECT 
                    r.id, r.sku, r.qty, r.status, p.id AS product_id
                FROM 
                    flashsale.reservation r 
                INNER JOIN 
                    flashsale.product p on p.sku=r.sku
                WHERE 
                    r.id=:rid FOR UPDATE
            """), {"rid": rid}).first()
            if not row or row.status != "pending":
                return  # idempotência básica

            # atualiza status para confirmed
            db.execute(text("UPDATE flashsale.reservation SET status='confirmed' WHERE id=:rid"), {"rid": rid})

            # ajusta estoque: reservado volta a diminuir (finalizou a compra)
            db.execute(text("""
                UPDATE 
                    flashsale.inventory 
                SET 
                    reserved = GREATEST(reserved - :qty, 0),
                    total    = GREATEST(total - :qty, 0)
                WHERE product_id = :pid
            """), {"qty": row.qty, "pid": row.product_id})


            # outbox event
            stmt = text("""
                INSERT INTO flashsale.outbox 
                    (aggregate_type, aggregate_id, event_type, payload_json, status,created_at, published_at)
                VALUES 
                    (:t, :id, :et, :p, :s,:ca, :pa)
            """).bindparams(
                bindparam("t"),
                bindparam("id"),
                bindparam("et"),
                bindparam("p", type_=JSONB),
                bindparam("s"),
                bindparam("ca"),
                bindparam("pa"),
            )
            
            db.execute(stmt, {
                "t": "reservation",
                "id": row.id,
                "et": "ReservationConfirmed",
                "p": json.dumps({"reservation_id": row.id}),
                "s": "pending",
                "ca": datetime.now(timezone.utc), 
                "pa": datetime.now(timezone.utc)   
            })
    except Exception as e:
        logging.error(f"error confirming reservation id={rid}: {e}", exc_info=True)

    

def run():
    params = pika.URLParameters(settings.RABBITMQ_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    # fila específica para confirmações (pode vir de payment service)
    ch.queue_declare(queue=QUEUE, durable=True,arguments={"x-single-active-consumer": True})
    ch.queue_bind(queue=QUEUE, exchange=EXCHANGE, routing_key=ROUTING)

    ch.basic_qos(prefetch_count=50)
    
    def cb(chx, method, props, body):
        try:
            handle_confirm(json.loads(body.decode()))
            chx.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e: 
            chx.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            logging.error(f"error processing message: {e}", exc_info=True)

    logging.info("waiting for messages...")
    ch.basic_consume(queue=QUEUE, on_message_callback=cb)
    ch.start_consuming()

if __name__ == "__main__":
    run()