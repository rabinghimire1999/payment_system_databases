"""V1 API Router.

This module aggregates all domain-specific routes (fpss, transactions, 
balances, webhooks) under a single router instance for the application.
"""

from fastapi import APIRouter, Depends
from app.api.v1.routes import fpss, transactions, balances, webhook
from app.api.v1.routes import member, member_transaction
from app.core.security import verify_api_key

api_router = APIRouter()
api_router.include_router(fpss.router, prefix="/internal/fps", tags=["fpss"], dependencies=[Depends(verify_api_key)])
api_router.include_router(transactions.router, prefix="/internal/transactions", tags=["transactions"], dependencies=[Depends(verify_api_key)])
api_router.include_router(balances.router, prefix="/internal/balances", tags=["balances"], dependencies=[Depends(verify_api_key)])
api_router.include_router(webhook.router, prefix="/internal/webhook", tags=["Webhook"], dependencies=[Depends(verify_api_key)])
api_router.include_router(member.router, prefix="/internal/member", tags=["members"], dependencies=[Depends(verify_api_key)])
api_router.include_router(member_transaction.router, prefix="/internal/member-transaction", tags=["member_transactions"], dependencies=[Depends(verify_api_key)])