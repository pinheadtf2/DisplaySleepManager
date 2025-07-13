import datetime
import time
import threading
from PIL import Image, ImageDraw
import pystray
import sys

# === CONFIGURABLE TIME SETTINGS ===
WAKE_START_WEEKDAYS = datetime.time(23, 8)   # 6:30 AM
WAKE_START_WEEKENDS = datetime.time(9, 0)    # 9:00 AM
WAKE_END_TIME = datetime.time(12, 0)         # 12:00 PM

done_event = threading.Event()

# === SYSTEM TRAY ICON ===
def create_image():
    # Create a simple green circle icon
    img = Image.new("RGB", (64, 64), color="black")
    d = ImageDraw.Draw(img)
    d.ellipse((16, 16, 48, 48), fill="green")
    return img


icon = pystray.Icon("WakeMonitor", icon=create_image(), title="Wake Monitor Script")

def quit_icon(icon):
    icon.stop()
    return

icon.menu = pystray.Menu(
    pystray.MenuItem("Exit", quit_icon)
)

# === WAKE FUNCTION ===
def is_weekend(day: datetime.datetime):
    return day.weekday() >= 5  # 5 = Saturday, 6 = Sunday

def in_wake_range(now, start, end):
    return start <= now.time() <= end

def wake_monitor():
    # Simulate mouse movement to wake monitor
    from ctypes import windll, Structure, c_long, byref

    class POINT(Structure):
        _fields_ = [("x", c_long), ("y", c_long)]

    def get_mouse_pos():
        pt = POINT()
        windll.user32.GetCursorPos(byref(pt))
        return pt.x, pt.y

    def set_mouse_pos(x, y):
        windll.user32.SetCursorPos(x, y)

    x, y = get_mouse_pos()
    set_mouse_pos(x + 1, y)
    time.sleep(0.05)
    set_mouse_pos(x, y)

# === MAIN LOGIC THREAD ===
def run_wake_logic():
    while True:
        now = datetime.datetime.now()
        today = now.date()

        # Determine next wake target time (today or tomorrow)
        weekend_today = is_weekend(now)
        wake_start_time = WAKE_START_WEEKENDS if weekend_today else WAKE_START_WEEKDAYS
        start_today = datetime.datetime.combine(today, wake_start_time)
        end_today = datetime.datetime.combine(today, WAKE_END_TIME)

        if now < start_today:
            # Too early, wait until today's wake window
            target = start_today
        elif start_today <= now <= end_today:
            # In today's wake window
            print(f"[{now}] In wake window. Waking monitor...")
            icon.title = "Waking monitor..."
            wake_monitor()
            break
        else:
            # Too late, schedule for tomorrow
            tomorrow = today + datetime.timedelta(days=1)
            weekend_tomorrow = is_weekend(datetime.datetime.combine(tomorrow, datetime.time()))
            target = datetime.datetime.combine(tomorrow, WAKE_START_WEEKENDS if weekend_tomorrow else WAKE_START_WEEKDAYS)

        # Wait until target
        goal_wait_seconds = (target - now).total_seconds()
        wait_seconds = max(goal_wait_seconds, 60)
        print(f"[{now}] Waiting {int(wait_seconds)} seconds until next wake window at {target.time()}...")
        icon.title = f"Waiting until {target.strftime('%a %H:%M')}"
        time.sleep(wait_seconds)

    icon.stop()
    return


# === RUN ===
if __name__ == "__main__":
    thread = threading.Thread(target=run_wake_logic)
    thread.start()
    icon.run_detached()  # Don't block main thread
    thread.join()
    sys.exit(0)
