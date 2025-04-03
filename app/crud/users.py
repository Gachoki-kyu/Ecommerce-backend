from sqlalchemy.orm import Session
from .. import models, schemas
from typing import Optional
from ..utils import get_password_hash, generate_referral_code


def get_all_users():
    return d
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()

def get_user_by_referral_code(db: Session, referral_code: str):
    return db.query(models.User).filter(models.User.referral_code == referral_code).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    referral_code = generate_referral_code(user.username)
    
    db_user = models.User(
        username=user.username,
        email=user.email,
        phone=user.phone,
        password=hashed_password,
        referral_code=referral_code,
        wallet_balance=50.0  # Initial bonus
    )
    
    if user.referral_code:
        referrer = get_user_by_referral_code(db, user.referral_code)
        if referrer:
            db_user.referred_by = referrer.id
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_wallet(db: Session, user_id: int, amount: float):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    db_user.wallet_balance += amount
    db.commit()
    db.refresh(db_user)
    return db_user

def apply_referral_bonus(db: Session, referrer_id: int):
    referrer = db.query(models.User).get(referrer_id)
    if referrer:
        referrer.wallet_balance += 50
        db.commit()
    return referrer