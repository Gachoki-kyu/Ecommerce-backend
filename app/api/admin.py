from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas,models
from typing import Optional
from ..database import get_db
from ..dependencies import get_admin_user
from ..crud import transactions, investments, users

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/reports")
def get_reports(
    db: Session = Depends(get_db),
    admin: schemas.UserOut = Depends(get_admin_user)
):
    # These would be more efficient with SQL aggregate functions
    total_deposits = sum(
        t.amount for t in db.query(models.Transaction)
        .filter(models.Transaction.type == "deposit", models.Transaction.status == "approved")
        .all()
    )
    
    total_withdrawals = sum(
        t.amount for t in db.query(models.Transaction)
        .filter(models.Transaction.type == "withdrawal", models.Transaction.status == "approved")
        .all()
    )
    
    total_investments = sum(i.amount for i in db.query(models.Investment).all())
    
    return {
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "total_investments": total_investments
    }

@router.post("/withdrawals/{transaction_id}/approve", response_model=schemas.TransactionOut)
def approve_withdrawal(
    transaction_id: int,
    db: Session = Depends(get_db),
    admin: schemas.UserOut = Depends(get_admin_user)
):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    if transaction.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction cannot be approved"
        )
    
    transaction.status = "approved"
    db.commit()
    return transaction

@router.post("/manage-user")
def manage_user(
    action: schemas.UserManage,
    db: Session = Depends(get_db),
    admin: schemas.UserOut = Depends(get_admin_user)
):
    user = users.get_user(db, user_id=action.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if action.action == "block":
        user.role = "blocked"
    elif action.action == "delete":
        db.delete(user)
    
    db.commit()
    return {"message": "User action completed"}
@router.get("/get-users")
def get_users(
    db: Session = Depends(get_db),
    admin: schemas.UserOut = Depends(get_admin_user),
    search: Optional[str]="",
    limit: int = 100, 
    skip: int = 0
    ):

    results = db.query(models.User).filter(models.User.username.contains(search)).limit(limit).offset(skip).all()
    # display = list(map(lambda x: x._asdict(), results))
    return results
