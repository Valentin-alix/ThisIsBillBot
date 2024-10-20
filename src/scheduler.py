import threading
from time import sleep

import schedule


def run_continuously(interval=5):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        def run(self):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run
