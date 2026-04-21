# Use of server.py → Runs the fake server (honeypot environment) that attackers interact with.

from fastapi import APIRouter
from honeypot.fake_login import router as login_router
from honeypot.api_trap import router as api_router

router = APIRouter()

router.include_router(login_router)
router.include_router(api_router)