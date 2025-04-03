from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models

router = APIRouter(prefix="/callbacks", tags=["callbacks"])

@router.post("/mpesa")
async def mpesa_callback(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    result = data.get("Body", {}).get("stkCallback", {})
    
    checkout_request_id = result.get("CheckoutRequestID")
    result_code = result.get("ResultCode")
    
    if result_code == "0":
        # Successful payment
        transaction = db.query(models.Transaction).filter(
            models.Transaction.reference == checkout_request_id
        ).first()
        
        if transaction:
            transaction.status = "completed"
            user = db.query(models.User).get(transaction.user_id)
            if user:
                user.wallet_balance += transaction.amount
            db.commit()
    
    return {"status": "received"}