from apscheduler.schedulers.blocking import BlockingScheduler
from scrape.runners import run_scrapers

def start_scheduler():
    scheduler = BlockingScheduler()

    # Run scraper every day at 09:00 AM
    scheduler.add_job(run_scrapers, 'cron', hour=9, minute=0)

    # Optional: run every hour instead
    # scheduler.add_job(run_scrapers, 'interval', hours=1)

    print("Scheduler started. Scrapers will run automatically.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")

if __name__ == "__main__":
    start_scheduler()
