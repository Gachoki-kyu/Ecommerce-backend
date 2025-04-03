from sqlalchemy.orm import Session
from .. import models, schemas

def get_user_cart(db: Session, user_id: int):
    return db.query(models.Cart).filter(models.Cart.user_id == user_id).first()

def create_user_cart(db: Session, user_id: int):
    db_cart = models.Cart(user_id=user_id)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart

def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int = 1):
    cart = get_user_cart(db, user_id)
    if not cart:
        cart = create_user_cart(db, user_id)
    
    # Check if product already in cart
    item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id,
        models.CartItem.product_id == product_id
    ).first()
    
    if item:
        item.quantity += quantity
    else:
        item = models.CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(item)
    
    db.commit()
    db.refresh(cart)
    return cart

def remove_from_cart(db: Session, item_id: int, user_id: int):
    cart = get_user_cart(db, user_id)
    if not cart:
        return None
    
    item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.cart_id == cart.id
    ).first()
    
    if item:
        db.delete(item)
        db.commit()
        return True
    return False