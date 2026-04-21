# Use of fake_login.py → Simulates a fake login system to capture credentials and login attempts.

from fastapi import APIRouter, Request
from honeypot.logger import log_attack
from ai_engine.predictor import predict

router = APIRouter()

@router.post("/login")
async def fake_login(request: Request):
    body = await request.json()
    text = str(body)

    attack_type, risk = predict(text)

    log_attack({
        "ip": request.client.host,
        "endpoint": "/login",
        "payload": text,
        "attack_type": attack_type,
        "risk": risk
    })

    return {"status": "Invalid credentials"}