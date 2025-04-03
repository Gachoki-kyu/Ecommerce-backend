from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, models
from ..crud import wishlist
from ..database import get_db
from ..dependencies import get_current_user, oauth2_scheme

router = APIRouter(prefix="/wishlist", tags=["wishlist"])

@router.post("/add", response_model=schemas.WishlistOut)
def add_to_wishlist(
    item: schemas.WishlistItemCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    return crud.wishlist.add_to_wishlist(db, user_id=current_user.id, product_id=item.product_id)

@router.get("/", response_model=schemas.WishlistOut)
def get_wishlist(
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    wishlist = crud.wishlist.get_user_wishlist(db, current_user.id)
    if not wishlist:
        raise HTTPException(404, "Wishlist not found")
    return wishlist

@router.delete("/item/{item_id}")
def remove_wishlist_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    return crud.wishlist.remove_from_wishlist(db, item_id=item_id, user_id=current_user.id)

@router.post("/item/{item_id}/move-to-cart", response_model=schemas.CartOut)
def move_to_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    # Get wishlist item
    wishlist_item = db.query(models.WishlistItem).filter(
        models.WishlistItem.id == item_id,
        models.WishlistItem.wishlist.has(user_id=current_user.id)
    ).first()
    
    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Item not found in wishlist")
    
    # Add to cart
    cart = crud.cart.add_to_cart(
        db, 
        user_id=current_user.id,
        product_id=wishlist_item.product_id
    )
    
    # Remove from wishlist
    db.delete(wishlist_item)
    db.commit()
    
    return cart