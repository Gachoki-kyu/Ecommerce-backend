from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, get_db
from .database import seed_products, seed_investment_plans
from . import models
from .services.scheduler import start_scheduler
from .services import weekly_fee
from .api import auth, investments, transactions, ecommerce, admin, cart, wishlist, payments, callbacks

models.Base.metadata.create_all(bind=engine)

db = next(get_db())
try:
    seed_investment_plans(db)
    seed_products(db)
finally:
    db.close()

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(investments.router)
app.include_router(transactions.router)
app.include_router(ecommerce.router)
app.include_router(admin.router)
app.include_router(cart.router)       
app.include_router(wishlist.router)
app.include_router(payments.router)
app.include_router(callbacks.router)

start_scheduler()
# Initialize the scheduler for investment maturity checks

@app.get("/")
def read_root():
    return {"message": "HydroFund API"}