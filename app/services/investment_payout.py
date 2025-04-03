from datetime import datetime
from sqlalchemy.orm import Session
from .. import models

def process_matured_investments(db: Session):
    try:
        investments = db.query(models.UserInvestment).filter(
            models.UserInvestment.end_date <= datetime.utcnow(),
            models.UserInvestment.is_matured == False
        ).all()

        payout_count = 0
        
        for investment in investments:
            user = investment.user
            total_payout = investment.amount_invested + investment.plan.total_income
            user.wallet_balance += total_payout
            investment.is_matured = True
            payout_count += 1
        
        db.commit()
        return {"message": f"Processed {payout_count} matured investments"}
    except Exception as e:
        db.rollback()
        raise e