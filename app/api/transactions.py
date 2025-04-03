from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas
from ..database import get_db
from ..dependencies import get_current_user
from ..crud import transactions, users
from ..services import payment as payment_service

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/deposit", response_model=schemas.TransactionOut, status_code=status.HTTP_201_CREATED)
async def create_deposit(
    deposit: schemas.TransactionBase,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    if deposit.type != "deposit":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction type must be 'deposit'"
        )
    
    # Process payment
    payment_result = await payment_service.process_payment("mpesa", deposit.amount, {})
    if payment_result["status"] != "success":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment processing failed"
        )
    
    # Update user wallet
    users.update_user_wallet(db, current_user.id, deposit.amount)
    
    # Create transaction
    transaction = transactions.create_transaction(
        db=db,
        transaction=deposit,
        user_id=current_user.id
    )
    transaction.status = "approved"
    db.commit()
    return transaction

@router.post("/withdrawal", response_model=schemas.TransactionOut, status_code=status.HTTP_201_CREATED)
def request_withdrawal(
    withdrawal: schemas.TransactionBase,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    if withdrawal.type != "withdrawal":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction type must be 'withdrawal'"
        )
    
    # Check max withdrawal limit
    if withdrawal.amount > 500000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Withdrawal exceeds the max limit of 500,000 Ksh"
        )
    
    # Check one withdrawal per day
    todays_withdrawal = transactions.get_todays_withdrawal(db, current_user.id)
    if todays_withdrawal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only one withdrawal is allowed per day"
        )
    
    # Apply 10% fee
    fee = withdrawal.amount * 0.10
    net_amount = withdrawal.amount - fee
    
    # Create withdrawal request
    withdrawal.fee_deducted = fee
    withdrawal.amount = net_amount
    return transactions.create_transaction(
        db=db,
        transaction=withdrawal,
        user_id=current_user.id
    )

@router.get("/", response_model=list[schemas.TransactionOut])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    return transactions.get_user_transactions(db, user_id=current_user.id)