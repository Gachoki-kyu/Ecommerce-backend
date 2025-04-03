from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db
from ..utils import verify_password, create_access_token
from ..crud import users

router = APIRouter(prefix="/auth", tags=["auth"])
#

@router.post("/signup", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user_email = users.get_user_by_email(db, email=user.email)
    db_user_phone = users.get_user_by_phone(db, phone=user.phone)
    if db_user_email or db_user_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with provided email or phone already exists"
        )
    if user.referral_code:
        referrer = users.get_user_by_referral_code(db, user.referral_code)
        if referrer:
            users.apply_referral_bonus(db, referrer.id)
    
    # Create user
    return users.create_user(db=db, user=user)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    db_user = users.get_user_by_phone(db, phone=form_data.username)
   
    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(
        data={"id": db_user.id, "role": db_user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}