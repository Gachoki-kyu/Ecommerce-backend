from datetime import datetime
from sqlalchemy.orm import Session
from .. import models

def deduct_weekly_fee(db: Session):
    try:
        users = db.query(models.User).filter(
            models.User.wallet_balance >= 50
        ).all()
        
        for user in users:
            user.wallet_balance -= 50
            user.last_fee_date = datetime.utcnow()
        
        db.commit()
        return {"message": f"Deducted fees from {len(users)} users"}
    except Exception as e:
        db.rollback()
        raise e