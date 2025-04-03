from sqlalchemy.orm import Session
from .. import models, schemas
from datetime import datetime, timedelta

def create_transaction(db: Session, transaction: schemas.TransactionBase, user_id: int):
    db_transaction = models.Transaction(
        user_id=user_id,
        **transaction.dict()
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_user_transactions(db: Session, user_id: int):
    return db.query(models.Transaction).filter(models.Transaction.user_id == user_id)\
           .order_by(models.Transaction.created_at.desc()).all()

def get_todays_withdrawal(db: Session, user_id: int):
    today = datetime.utcnow().date()
    return db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.type == "withdrawal",
        models.Transaction.created_at >= today
    ).first()