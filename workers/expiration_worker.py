import json, time
from sqlalchemy import text
from db.database import SessionLocal

BATCH = 200
SLEEP = 2  # segundos

def run():
    while True:
        with SessionLocal() as db:
            rows = db.execute(text("""
                SELECT id, product_id, qty
                FROM reservation
                WHERE status='pending' AND expires_at < NOW()
                ORDER BY id
                LIMIT :n
            """), {"n": BATCH}).fetchall()

            if not rows:
                time.sleep(SLEEP); continue

            for r in rows:
                try:
                    with db.begin():
                        # marca como expirado (idempotente)
                        updated = db.execute(text("""
                            UPDATE reservation
                            SET status='expired'
                            WHERE id=:rid AND status='pending'
                        """), {"rid": r.id}).rowcount
                        if updated == 0:
                            continue

                        # devolve estoque
                        db.execute(text("""
                            UPDATE inventory
                            SET reserved  = GREATEST(reserved - :qty, 0),
                                available = available + :qty
                            WHERE product_id = :pid
                        """), {"qty": r.qty, "pid": r.product_id})

                        # outbox event
                        db.execute(text("""
                            INSERT INTO outbox_event (aggregate_type, aggregate_id, event_type, payload_json, status)
                            VALUES ('reservation', :rid, 'ReservationExpired',
                                    :payload::jsonb, 'pending')
                        """), {"rid": r.id, "payload": json.dumps({"reservation_id": r.id})})
                except Exception:
                    pass
        # pequeno respiro
        time.sleep(SLEEP)

if __name__ == "__main__":
    run()
