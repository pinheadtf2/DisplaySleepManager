import logging
import datetime
import threading
import time

WAKE_NORMAL = datetime.time(6, 30)
WAKE_WEEKENDS = datetime.time(9, 0)
SLEEP_START = datetime.time(22, 0)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
done_event = threading.Event()


def get_weekends(now: datetime.datetime):
    tomorrow = now + datetime.timedelta(days=1)
    return now.weekday() >= 5, tomorrow.weekday() >= 5


def main():
    now = datetime.datetime.now()
    today = now.date()
    tomorrow = now + datetime.timedelta(days=1)

    # key concepts:
    # find if
    # wait until sleep trigger time OR immediately sleep display if currently before alarms are fired
    # sleep at sleep trigger time OR immediately if currently before alarms are fired
    # wait until

    # check if its a weekend today
    if today.weekday() >= 5:
        wake_time = WAKE_WEEKENDS
        debug_string = "Today is a weekend"
    else:
        wake_time = WAKE_NORMAL
        debug_string = "Today is NOT a weekend"

    wake_basis = today
    logger.debug(f"{debug_string}, time set to {wake_time}")

    # check if it is before the wake timer today
    wake_target = datetime.datetime.combine(wake_basis, wake_time)
    if now < wake_target:
        sleep_duration = (wake_target - now).total_seconds()
        logger.debug(f"Wake up time is valid for today")
    else:
        # it is after today's wake time and the sleep time, so wait for tomorrow's wake time
        logger.debug("Today's wake up time is invalid, swapping to tomorrow")
        if tomorrow.weekday() >= 5:
            wake_time = WAKE_WEEKENDS
            debug_string = "Tomorrow is a weekend"
        else:
            wake_time = WAKE_NORMAL
            debug_string = "Tomorrow is NOT a weekend"
        wake_basis = tomorrow.date()
        wake_target = datetime.datetime.combine(wake_basis, wake_time)
        logger.debug(f"{debug_string}, time set to {wake_time}")

    sleep_target = datetime.datetime.combine(today, SLEEP_START)
    if sleep_target < wake_target:
        logger.debug(f"It is before ")

    sleep_duration = (wake_target - now).total_seconds()
    logger.debug(f"Sleeping for {sleep_duration} seconds")
    time.sleep(sleep_duration)


if __name__ == '__main__':
    main()
