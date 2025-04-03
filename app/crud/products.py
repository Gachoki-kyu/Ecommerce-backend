from sqlalchemy.orm import Session
from .. import models, schemas

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()
    # return db.query(models.Product).all()

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def update_product_stock(db: Session, product_id: int, quantity: int, amount: float):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return None
    
    product.stock -= quantity
    product.earnings += amount
    db.commit()
    db.refresh(product)
    return product

def purchase_product(db: Session, product_id: int, user_id: int, quantity: int = 1):
    # Get product
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product or product.stock < quantity:
        return None
    
    # Get user
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    
    # Calculate total cost
    total_cost = product.price * quantity
    
    # Check sufficient balance
    if user.wallet_balance < total_cost:
        return None
    
    # Process transaction
    user.wallet_balance -= total_cost
    product.stock -= quantity
    product.earnings += total_cost
    
    # Create transaction record
    transaction = models.Transaction(
        user_id=user_id,
        type="purchase",
        amount=total_cost,
        status="completed",
        description=f"Purchased {quantity} of {product.name}"
    )
    
    db.add(transaction)
    db.commit()
    
    return {
        "product": product,
        "new_balance": user.wallet_balance,
        "transaction": transaction
    }