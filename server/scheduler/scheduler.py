from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from routers.admin import daily_sync_schedule
import settings

# A scheduler that runs on an asyncio (:pep:`3156`) event loop.
scheduler = AsyncIOScheduler()

def start_scheduler():
  """
  Initialize and start APScheduler in the background.
  """
  # now = datetime.now() + timedelta(seconds=30)  # 10 seconds in the future
  # print("now: ", now)
  scheduler.add_job(
    daily_sync_schedule,
    CronTrigger(hour=settings.DAILY_SYNC_HOUR),  # run daily at 20:00 local system timezone 
    # IntervalTrigger(seconds=30),  # runs every 30 seconds
    id="daily_extract", 
    replace_existing=True,
    misfire_grace_time=settings.MISFIRE_GRACE_TIME,        # give 1-hour grace in case of downtime # this should be in settings.py
  )
  scheduler.start()
  print("APScheduler started the daily sync.")
