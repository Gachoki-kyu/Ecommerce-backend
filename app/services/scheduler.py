from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from ..database import get_db
from .weekly_fee import deduct_weekly_fee
from .investment_payout import process_matured_investments
import logging
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED

scheduler = BackgroundScheduler()

def start_scheduler():
    # Weekly fee deduction (every Sunday at midnight)
    scheduler.add_job(
        lambda: deduct_weekly_fee(next(get_db())),
        trigger='cron',
        day_of_week='sun',
        hour=0,
        minute=0
    )

    # Investment maturity checks (every hour)
    scheduler.add_job(
        lambda: process_matured_investments(next(get_db())),
        trigger=IntervalTrigger(days=7)
    )

    scheduler.start()
 
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

def scheduler_listener(event):
    if event.exception:
        print(f"Job crashed: {event.job_id}")
        print(f"Error: {event.exception}")
        print(f"Traceback: {event.traceback}")

scheduler.add_listener(scheduler_listener, EVENT_JOB_ERROR | EVENT_JOB_MISSED)
