import datetime
import logging
import subprocess
import sys
import time
from ctypes import windll, Structure, c_long, byref

from PIL import Image
from pystray import Icon, Menu, MenuItem

WAKE_NORMAL = datetime.time(6, 30)
WAKE_WEEKENDS = datetime.time(9, 0)
SLEEP_START = datetime.time(22, 0)

# Create a logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('displaymanager.latest.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def on_quit(icon):
    icon.stop()
    sys.exit(0)


def create_tray_icon():
    image = Image.open("favicon.ico")
    menu = Menu(MenuItem('Quit', on_quit))
    icon = Icon('Display Manager', image, 'Display Manager', menu)
    icon.run_detached()


def sleep_monitor():
    logger.info("Issuing display sleep in 15 seconds")
    time.sleep(15)
    subprocess.Popen("doff.exe")


def wake_monitor():
    class POINT(Structure):
        _fields_ = [("x", c_long), ("y", c_long)]

    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    windll.user32.SetCursorPos(pt.x + 1, pt.y)
    time.sleep(0.05)
    windll.user32.SetCursorPos(pt.x, pt.y)


def main():
    now = datetime.datetime.now()
    today = now.date()
    tomorrow = now + datetime.timedelta(days=1)
    wake_today = WAKE_WEEKENDS if now.weekday() >= 5 else WAKE_NORMAL
    wake_tomorrow = WAKE_WEEKENDS if tomorrow.weekday() >= 5 else WAKE_NORMAL
    logger.info(f"Today's wake time is {wake_today.strftime('%I:%M:%S %p')}, "
                f"tomorrow's is {wake_tomorrow.strftime('%I:%M:%S %p')}")

    next_sleep = datetime.datetime.combine(today, SLEEP_START)
    timers = [
        (next_sleep, "sleep"),
        (datetime.datetime.combine(today, wake_today), "wake"),
        (datetime.datetime.combine(tomorrow, wake_tomorrow), "wake"),
        (datetime.datetime.combine(tomorrow, SLEEP_START), "sleep")
    ]

    next_timer = None
    next_action = None
    for timer, action in timers:
        if now < timer:
            next_timer = timer
            next_action = action
            break
    logger.info(f"Next timer is {next_timer.strftime("%m-%d-%Y %I:%M:%S %p")} with action {next_action}")

    if now > next_sleep:
        logger.info("It's quiet hours")
        sleep_monitor()

    sleep_duration = (next_timer - now).total_seconds()+5
    logger.info(f"Sleeping for {sleep_duration} seconds")
    time.sleep(sleep_duration)

    if next_action == "wake":
        logger.info("Waking up")
        wake_monitor()
    else:
        sleep_monitor()

    return


if __name__ == '__main__':
    create_tray_icon()
    while True:
        main()