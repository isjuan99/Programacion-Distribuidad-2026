from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.wishlist import LoyaltyTransaction

router = APIRouter(prefix="/users/me/loyalty", tags=["loyalty"])


class LoyaltyTransactionResponse(BaseModel):
    id: int
    points: int
    type: str
    description: str | None
    order_id: int | None
    created_at: datetime
    model_config = {"from_attributes": True}


class LoyaltySummaryResponse(BaseModel):
    balance: int
    transactions: List[LoyaltyTransactionResponse]


@router.get("", response_model=LoyaltySummaryResponse)
async def get_loyalty(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transactions = (
        db.query(LoyaltyTransaction)
        .filter(LoyaltyTransaction.user_id == current_user.id)
        .order_by(LoyaltyTransaction.created_at.desc())
        .limit(50)
        .all()
    )
    return LoyaltySummaryResponse(
        balance=current_user.loyalty_points or 0,
        transactions=transactions,
    )
