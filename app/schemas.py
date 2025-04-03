from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: str

class UserCreate(UserBase):
    password: str
    referral_code: Optional[str] = None

class UserLogin(BaseModel):
    phone: str
    password: str

class UserOut(UserBase):
    id: int
    wallet_balance: float
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class InvestmentPlanBase(BaseModel):
    name: str
    price: float
    cycle_days: int
    daily_income: float
    total_income: float
    automatic_reinvestment: bool = False

class InvestmentPlanCreate(InvestmentPlanBase):
    pass

class InvestmentPlanOut(InvestmentPlanBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserInvestmentBase(BaseModel):
    plan_id: int

class UserInvestmentOut(UserInvestmentBase):
    id: int
    user_id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str
    plan: InvestmentPlanOut
    
    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    type: str
    amount: float
    fee_deducted: float = 0.0
    description: Optional[str] = None

class TransactionOut(TransactionBase):
    id: int
    user_id: int
    fee_deducted: float
    sender: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    investment_cycle_days: int
    daily_income: float
    total_income: float
    stock: int = 0

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    earnings: float
    created_at: datetime

    class Config:
        from_attributes = True
class UserManage(BaseModel):
    user_id: int
    action: Literal["block","delete"] # 'block', 'delete'

class TransactionCreate(TransactionBase):
    status: str = "pending"
    sender: str = "EnergyEdge Ventures"

class ProductPurchase(BaseModel):
    quantity: int = 1  # Default to 1 if not specified

class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemCreate(CartItemBase):
    pass

class CartItemOut(CartItemBase):
    id: int
    product: ProductOut
    
    class Config:
        from_attributes = True

class CartOut(BaseModel):
    id: int
    user_id: int
    items: list[CartItemOut] = []
    
    class Config:
        from_attributes = True

class WishlistItemBase(BaseModel):
    product_id: int

class WishlistItemCreate(WishlistItemBase):
    pass

class WishlistItemOut(WishlistItemBase):
    id: int
    product: ProductOut
    
    class Config:
        from_attributes = True

class WishlistOut(BaseModel):
    id: int
    user_id: int
    items: list[WishlistItemOut] = []
    
    class Config:
        from_attributes = True

class PaymentRequest(BaseModel):
    phone_number: str
    amount: float
    description: str

class PaymentStatusResponse(BaseModel):
    status: str
    transaction: Optional[TransactionOut] = None
    details: Optional[dict] = None