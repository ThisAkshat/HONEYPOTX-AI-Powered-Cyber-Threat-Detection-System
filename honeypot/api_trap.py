# Use of api_trap.py → Creates fake API endpoints to capture malicious requests and payloads.

from fastapi import APIRouter, Request
from honeypot.logger import log_attack
from ai_engine.predictor import predict

router = APIRouter()

@router.post("/api/data")
async def api_trap(request: Request):
    body = await request.json()
    text = str(body)

    attack_type, risk = predict(text)

    log_attack({
        "ip": request.client.host,
        "endpoint": "/api/data",
        "payload": text,
        "attack_type": attack_type,
        "risk": risk
    })

    return {"data": "fake response"}