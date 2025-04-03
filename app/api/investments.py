from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas
from ..database import get_db
from ..dependencies import get_current_user
from ..crud import investments as crud_investments

router = APIRouter(prefix="/investments", tags=["investments"])

@router.get("/plans", response_model=list[schemas.InvestmentPlanOut])
def get_plans(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    return crud_investments.get_investment_plans(db, skip=skip, limit=limit)

@router.post("/invest", response_model=schemas.UserInvestmentOut)
def invest_in_plan(
    investment: schemas.UserInvestmentBase,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    db_investment = crud_investments.create_user_investment(db, investment, current_user.id)
    if not db_investment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Investment failed - insufficient balance or invalid plan"
        )
    return db_investment

@router.get("/my-investments", response_model=list[schemas.UserInvestmentOut])
def get_my_investments(
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    return crud_investments.get_user_investments(db, current_user.id)