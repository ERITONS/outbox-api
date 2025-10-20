from datetime import datetime, timezone
import json, time, logging
from sqlalchemy import text, bindparam
from app.db.database import SessionLocal
from sqlalchemy.dialects.postgresql import JSONB


BATCH = 200
SLEEP = 2  # segundos

def run():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [expiration] %(levelname)s: %(message)s")
    logging.info("starting expiration worker...")
    while True:
        with SessionLocal() as db:
            rows = db.execute(text("""
                SELECT reservation.id, reservation.sku, reservation.qty, p.id AS product_id
                FROM flashsale.reservation
                INNER JOIN flashsale.product p on p.sku=reservation.sku                   
                WHERE reservation.status='pending' AND reservation.expires_at < NOW()
                ORDER BY id
                LIMIT :n
            """), {"n": BATCH}).fetchall()

            if not rows:
                time.sleep(SLEEP); continue

            for r in rows:
                try:
                    logging.info(f"expiring reservation id={r.id} (sku={r.sku})")
                    with SessionLocal.begin() as db:
                        # marca como expirado (idempotente)
                        updated = db.execute(text("""
                            UPDATE flashsale.reservation
                            SET status='expired'
                            WHERE id=:rid AND status='pending'
                        """), {"rid": r.id}).rowcount
                        if updated == 0:
                            continue

                        # devolve estoque
                        db.execute(text("""
                            UPDATE flashsale.inventory
                            SET reserved  = GREATEST(reserved - :qty, 0),
                                available = available + :qty
                            WHERE product_id = :pid
                        """), {"qty": r.qty, "pid": r.product_id})

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
                            "id": r.id,
                            "et": "ReservationExpired",
                            "p": json.dumps({"reservation_id": r.id}),
                            "s": "pending",
                            "ca": datetime.now(timezone.utc), 
                            "pa": datetime.now(timezone.utc),

                        })

                except Exception as e:
                    logging.error(f"error expiring reservation id={r.id}: {e}")
        # pequeno respiro
        time.sleep(SLEEP)

if __name__ == "__main__":
    run()
