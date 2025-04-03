from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services.mpesa import MpesaGateway
from ..database import get_db
from ..dependencies import get_current_user
from .. import schemas, models

router = APIRouter(prefix="/payments", tags=["payments"])
mpesa = MpesaGateway()

@router.post("/initiate-stk")
async def initiate_stk_push(
    payment: schemas.PaymentRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        # Format phone number (remove + and add country code if needed)
        phone = payment.phone_number.strip().replace("+", "").replace(" ", "")
        if not phone.startswith("254"):
            phone = f"254{phone[-9:]}"  # Convert to 254 format
        
        response = mpesa.stk_push(
            phone=phone,
            amount=payment.amount,
            account_ref=f"user_{current_user.id}",
            description=payment.description
        )
        
        # Save transaction record
        transaction = models.Transaction(
            user_id=current_user.id,
            type="deposit",
            amount=payment.amount,
            status="pending",
            reference=response["CheckoutRequestID"],
            description=f"MPesa deposit: {payment.description}"
        )
        db.add(transaction)
        db.commit()
        
        return {
            "message": "Payment initiated",
            "checkout_request_id": response["CheckoutRequestID"],
            "merchant_request_id": response["MerchantRequestID"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{checkout_request_id}")
async def check_payment_status(
    checkout_request_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        # First check our database
        transaction = db.query(models.Transaction).filter(
            models.Transaction.reference == checkout_request_id,
            models.Transaction.user_id == current_user.id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        if transaction.status == "completed":
            return {"status": "completed", "transaction": transaction}
        
        # Check with M-Pesa
        response = mpesa.check_payment_status(checkout_request_id)
        
        if response.get("ResultCode") == "0":
            transaction.status = "completed"
            current_user.wallet_balance += transaction.amount
            db.commit()
            return {"status": "completed", "transaction": transaction}
        
        return {"status": "pending", "details": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))