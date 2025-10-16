from fastapi import APIRouter
from . import cache_demo

api_router = APIRouter(prefix="/api")
api_router.include_router(cache_demo.router)
