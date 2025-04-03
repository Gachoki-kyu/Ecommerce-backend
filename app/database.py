from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
from .base import Base
from . import models


load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_products(db: Session):
    products_data = [
        {
            "name": "SAFE OIL FIELD",
            "description": "Low-risk oil field investment",
            "price": 45000,
            "investment_cycle_days": 7,
            "daily_income": 60000,
            "total_income": 420000,
            "stock": 10
        },
        {
            "name": "GRANDE OILFIELD",
            "description": "Medium-term oil field investment",
            "price": 90000,
            "investment_cycle_days": 30,
            "daily_income": 14400,
            "total_income": 432000,
            "stock": 5
        },
        {
            "name": "Welfare Products.4",
            "description": "Short-term high-yield investment",
            "price": 180000,
            "investment_cycle_days": 5,
            "daily_income": 144000,
            "total_income": 720000,
            "stock": 3
        },
        {
            "name": "Senior Partner",
            "description": "Premium long-term investment",
            "price": 450000,
            "investment_cycle_days": 30,
            "daily_income": 72000,
            "total_income": 2160000,
            "stock": 2
        },
        {
            "name": "Oasis Solar Farm",
            "description": "Renewable energy investment",
            "price": 54000,
            "investment_cycle_days": 15,
            "daily_income": 4800,
            "total_income": 72000,
            "stock": 8
        }
    ]
    
    for product_data in products_data:
        if not db.query(models.Product).filter(models.Product.name == product_data["name"]).first():
            db_product = models.Product(**product_data)
            db.add(db_product)
    db.commit()

def seed_investment_plans(db: Session):
    plans_data = [
        {"name": "M-pesa Partnership Project",
         "price": 16200,
         "cycle_days": 10,
         "daily_income": 15600,
         "total_income": 156000},
        {"name": "Hebron Oil Field",
         "price": 13320,
         "cycle_days": 30,
         "daily_income": 1368,
         "total_income": 41040},
        # Add all other plans from your table
        {"name": "New User Products 2",
         "price": 750,
         "cycle_days": 3,
         "daily_income": 336,
         "total_income": 1008},
        {"name": "Buffett Fund-1",
         "price": 4560,
         "cycle_days": 10,
         "daily_income": 3000,
         "total_income": 30000},
        {"name": "Welfare Products",
         "price": 8550,
         "cycle_days": 10,
         "daily_income": 7080, 
         "total_income": 70800}
    ]
    
    for plan_data in plans_data:
        if not db.query(models.InvestmentPlan).filter(models.InvestmentPlan.name == plan_data["name"]).first():
            db_plan = models.InvestmentPlan(**plan_data)
            db.add(db_plan)
    
    db.commit()