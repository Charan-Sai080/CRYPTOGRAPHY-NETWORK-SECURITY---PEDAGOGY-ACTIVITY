from __future__ import annotations

from fastapi import APIRouter

from backend.api.v1.dsa import router as dsa_router
from backend.api.v1.elgamal import router as elgamal_router
from backend.api.v1.lcg import router as lcg_router
from backend.api.v1.otp import router as otp_router

api_v1_router = APIRouter()
api_v1_router.include_router(otp_router)
api_v1_router.include_router(lcg_router)
api_v1_router.include_router(elgamal_router)
api_v1_router.include_router(dsa_router)
