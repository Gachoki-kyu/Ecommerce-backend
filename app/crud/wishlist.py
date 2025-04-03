from sqlalchemy.orm import Session
from .. import models, schemas

def get_user_wishlist(db: Session, user_id: int):
    return db.query(models.Wishlist).filter(models.Wishlist.user_id == user_id).first()

def create_user_wishlist(db: Session, user_id: int):
    db_wishlist = models.Wishlist(user_id=user_id)
    db.add(db_wishlist)
    db.commit()
    db.refresh(db_wishlist)
    return db_wishlist

def add_to_wishlist(db: Session, user_id: int, product_id: int):
    wishlist = get_user_wishlist(db, user_id)
    if not wishlist:
        wishlist = create_user_wishlist(db, user_id)
    
    # Check if product already in wishlist
    existing = db.query(models.WishlistItem).filter(
        models.WishlistItem.wishlist_id == wishlist.id,
        models.WishlistItem.product_id == product_id
    ).first()
    
    if existing:
        return wishlist
    
    item = models.WishlistItem(
        wishlist_id=wishlist.id,
        product_id=product_id
    )
    db.add(item)
    db.commit()
    db.refresh(wishlist)
    return wishlist

def remove_from_wishlist(db: Session, item_id: int, user_id: int):
    wishlist = get_user_wishlist(db, user_id)
    if not wishlist:
        return None
    
    item = db.query(models.WishlistItem).filter(
        models.WishlistItem.id == item_id,
        models.WishlistItem.wishlist_id == wishlist.id
    ).first()
    
    if item:
        db.delete(item)
        db.commit()
        return True
    return False