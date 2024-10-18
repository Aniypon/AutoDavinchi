import os
import subprocess
import sys

from loguru import logger


async def update_stat(self):
    try:
        os.system(f'title "QueVinchik - Подходящие {self.suitable_forms} | Скип {self.skipped_forms} | Всего {self.all_forms}"')
    except:
        pass


def notify(self):
    if self.config["notify"]["move_on_top"]:
        try:
            process = subprocess.Popen(["xdotool", "getactivewindow"], stdout=subprocess.PIPE)
            window_id, _ = process.communicate()
            subprocess.Popen(["wmctrl", "-i", "-r", window_id.strip(), "-b", "add,above"])
        except:
            pass

    if self.config["notify"]["send_notify"]:
        try:
            self.toast.show_toast("QueVinchik", "Найдена подходящая анкета", duration=10, threaded=True)
        except:
            pass


def setup_logger():
    logger.add(sys.stdout, colorize=True, enqueue=True, backtrace=True, diagnose=True)
    logger.remove(0)
