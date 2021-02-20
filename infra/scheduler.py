import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from utils.logger import logger

aio_scheduler = None

def set_scheduler(scheduler: AsyncIOScheduler):
    global aio_scheduler
    aio_scheduler = scheduler

def new_scheduler(loop):
    if loop != None:
        return AsyncIOScheduler(event_loop=loop)
    return AsyncIOScheduler()

def get_scheduler():
    return aio_scheduler

def init_scheduler(loop):
    scheduler = new_scheduler(loop)
    set_scheduler(scheduler)
    scheduler.start()
    logger.info("<infra> scheduler initialized")

if __name__ == '__main__':
    def say_hello():
        print('hello')
    scheduler = AsyncIOScheduler()
    scheduler.scheduled_job('interval', seconds=1)(say_hello)
    scheduler.start()
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass