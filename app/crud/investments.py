from sqlalchemy.orm import Session, joinedload
from .. import models, schemas
from datetime import datetime, timedelta

def get_investment_plans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.InvestmentPlan).filter(models.InvestmentPlan.is_active == True).offset(skip).limit(limit).all()

def get_investment_plan(db: Session, plan_id: int):
    return db.query(models.InvestmentPlan).filter(models.InvestmentPlan.id == plan_id).first()

def create_user_investment(db: Session, investment: schemas.UserInvestmentBase, user_id: int):
    # Get the plan
    plan = db.query(models.InvestmentPlan).filter(models.InvestmentPlan.id == investment.plan_id).first()
    if not plan:
        return None
    
    # Get user
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    
    # Check sufficient balance
    if user.wallet_balance < plan.price:
        return None
    
    # Deduct from wallet
    user.wallet_balance -= plan.price
    
    # Create investment
    end_date = datetime.utcnow() + timedelta(days=plan.cycle_days)
    db_investment = models.UserInvestment(
        user_id=user_id,
        plan_id=plan.id,
        amount_invested=plan.price,
        end_date=end_date
    )
    
    db.add(db_investment)
    db.commit()
    db.refresh(db_investment)
    return db_investment

def get_user_investments(db: Session, user_id: int):
    return (
    db.query(models.UserInvestment)
    .options(joinedload(models.UserInvestment.plan))
    .filter(models.UserInvestment.user_id == user_id).all()
    )