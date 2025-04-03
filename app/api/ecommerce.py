from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models, crud
from ..database import get_db
from ..dependencies import get_current_user
from ..crud import products, transactions, users

router = APIRouter(prefix="/ecommerce", tags=["ecommerce"])

@router.get("/products", response_model=list[schemas.ProductOut])
def get_products(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    # products= db.query(models.Product).offset(skip).limit(limit).all()
    return products.get_products(db, skip=skip, limit=limit)

@router.get("/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.post("/products/{product_id}/purchase")
def purchase_product(
    purchase: schemas.ProductPurchase,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Get product
    product = db.query(models.Product).get(product_id)
    if not product or product.stock < purchase.quantity:
        raise HTTPException(400, "Product unavailable")

    # Calculate total cost
    total = product.price * purchase.quantity
    
    # Check balance
    if current_user.wallet_balance < total:
        raise HTTPException(400, "Insufficient balance")

    # Process purchase
    current_user.wallet_balance -= total
    product.stock -= purchase.quantity
    
    # Record transaction
    transaction = models.Transaction(
        user_id=current_user.id,
        type="purchase",
        amount=total,
        status="completed",
        description=f"Purchased {purchase.quantity} {product.name}"
    )
    
    db.add(transaction)
    db.commit()
    return {"message": "Purchase successful", "new_balance": current_user.wallet_balance}

@router.post("/checkout", response_model=schemas.TransactionOut)
def checkout_cart(
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    # Get user's cart
    cart = crud.cart.get_user_cart(db, current_user.id)
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate total
    total = sum(item.product.price * item.quantity for item in cart.items)
    
    # Check balance
    if current_user.wallet_balance < total:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Process each item
    for item in cart.items:
        # Deduct from stock
        item.product.stock -= item.quantity
        if item.product.stock < 0:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {item.product.name}")
        
        # Record transaction
        transaction = models.Transaction(
            user_id=current_user.id,
            type="purchase",
            amount=item.product.price * item.quantity,
            status="completed",
            description=f"Purchased {item.quantity} of {item.product.name}"
        )
        db.add(transaction)
    
    # Clear cart
    db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id).delete()
    db.commit()
    
    return transaction