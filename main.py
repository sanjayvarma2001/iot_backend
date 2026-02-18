import time
import json
from fastapi import FastAPI, Depends
import os
import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session
from datetime import datetime
import model
import db
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_db():
    retry_count = 10
    while retry_count > 0:
        try:
            model.Base.metadata.create_all(bind=db.engine)
            return
        except Exception as e:
            retry_count -= 1
            if retry_count > 0:
                time.sleep(2)
    exit(1)


init_db()

MQTT_BROKER = os.environ.get("MQTT_BROKER_HOST", "127.0.0.1")


def serialize_row(r):
    """Convert SQLAlchemy ORM row to JSON-serializable dict."""
    data = {}
    for c in r.__table__.columns:
        val = getattr(r, c.key, None)
        if isinstance(val, datetime):
            val = val.isoformat()
        data[c.key] = val
    return data


def on_message(client, userdata: None, msg):
    session = db.SessionLocal()
    try:
        payload = json.loads(msg.payload)
        topic_parts = msg.topic.split("/")
        device_id = topic_parts[-1]

        new_logs = model.DeviceLogs(
            device_id=device_id,
            topic=msg.topic,
            temperature=payload.get("temperature"),
            humidity=payload.get("humidity"),
            pressure=payload.get("pressure"),
            voltage=payload.get("voltage"),
            current=payload.get("current"),
            timestamp=payload.get("timestamp")
        )
        session.add(new_logs)

        # Create alert if temperature exceeds threshold
        if payload.get("temperature", 0) > 50:
            new_alerts = model.Alerts(
                device_id=device_id,
                topic=msg.topic,
                alert="Critical Temperature",
                actual_value=payload.get("temperature"),
                threshold=50.0,
                severity="Critical",
                is_resolved=0,
                timestamp=payload.get("timestamp")
            )
            session.add(new_alerts)

        session.commit()
    except Exception as e:
        pass
    finally:
        session.close()


mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, 1883, 60)
mqtt_client.subscribe("sensors/data/#")
mqtt_client.loop_start()


@app.get("/logs")
def get_logs(db: Session = Depends(db.get_db)):
    rows = db.query(model.DeviceLogs).order_by(model.DeviceLogs.timestamp.desc()).limit(50).all()
    return [serialize_row(r) for r in rows]


@app.get("/alerts")
def get_alerts(db: Session = Depends(db.get_db)):
    rows = db.query(model.Alerts).order_by(model.Alerts.timestamp.desc()).all()
    return [serialize_row(r) for r in rows]


@app.get("/health")
def get_health(session: Session = Depends(db.get_db)):
    try:
        session.execute(text('SELECT 1'))
        return {
            "status": "active",
            "database": "connected",
            "mqtt broker": "running"
        }
    except Exception as e:
        return {
            "status": "inactive",
            "database": "disconnected",
            "error": str(e)
        }, 500
