from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..crud import cart
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])

@router.post("/add", response_model=schemas.CartOut)
def add_to_cart(
    item: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    return crud.cart.add_to_cart(db, user_id=current_user.id, product_id=item.product_id, quantity=item.quantity)

@router.get("/", response_model=schemas.CartOut)
def get_cart(
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    cart = crud.cart.get_user_cart(db, current_user.id)
    if not cart:
        raise HTTPException(404, "Cart not found")
    return cart

@router.delete("/item/{item_id}")
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    return crud.cart.remove_from_cart(db, item_id=item_id, user_id=current_user.id)