from fastapi import APIRouter
from . import admin_auth, customer_auth ,token_auth


router = APIRouter()


router.include_router(admin_auth.router)
router.include_router(customer_auth.router)
router.include_router(token_auth.router)
