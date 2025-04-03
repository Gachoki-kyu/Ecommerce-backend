from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    two_factor_secret = Column(String)
    wallet_balance = Column(Float, default=0.0)
    referral_code = Column(String)
    referred_by = Column(Integer, ForeignKey('users.id'))
    role = Column(String, default="admin")  # 'user', 'admin', 'blocked'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    investments = relationship("UserInvestment", back_populates="user")
    last_fee_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    transactions = relationship("Transaction", back_populates="user")
class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    plan = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    duration = Column(Integer, nullable=False)  # in hours
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="active")  # 'active', 'completed', 'cancelled'
    automatic_reinvestment = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    type = Column(String, nullable=False)  # 'deposit', 'withdrawal', 'investment', 'bonus', 'purchase'
    amount = Column(Float, nullable=False)
    fee_deducted = Column(Float, default=0.0)
    sender = Column(String, default="EnergyEdge Ventures")
    status = Column(String, default="pending")  # 'pending', 'approved', 'declined'
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="transactions")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    investment_cycle_days = Column(Integer, nullable=False)
    daily_income = Column(Float, nullable=False)
    total_income = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    earnings = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
class InvestmentPlan(Base):
    __tablename__ = "investment_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    price = Column(Float, nullable=False)  # Initial investment amount
    cycle_days = Column(Integer, nullable=False)
    daily_income = Column(Float, nullable=False)
    total_income = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserInvestment(Base):
    __tablename__ = "user_investments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plan_id = Column(Integer, ForeignKey('investment_plans.id'), nullable=False)
    amount_invested = Column(Float, nullable=False)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True))
    status = Column(String, default="active")  # active, completed, cancelled
    last_payout = Column(DateTime(timezone=True))
    is_matured = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="investments")
    plan = relationship("InvestmentPlan", backref="user_investments",lazy="joined")

class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    items = relationship("CartItem", back_populates="cart")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey('carts.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)
    
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")

class Wishlist(Base):
    __tablename__ = "wishlists"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    items = relationship("WishlistItem", back_populates="wishlist")

class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    
    id = Column(Integer, primary_key=True)
    wishlist_id = Column(Integer, ForeignKey('wishlists.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    
    wishlist = relationship("Wishlist", back_populates="items")
    product = relationship("Product")