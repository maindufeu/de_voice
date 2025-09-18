from fastapi import APIRouter
from api.v1.endpoints import chat, call, retrieving

api_router = APIRouter()

api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(call.router, tags=["call"])
api_router.include_router(retrieving.router, prefix="/assets", tags=["assets"])