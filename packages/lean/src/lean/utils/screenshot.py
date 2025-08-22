import os
import re
import subprocess
import threading
from datetime import datetime

from .paths import app_screenshots_dir


def take_screenshot(on_result, on_cancel, on_error):
    thread = threading.Thread(
        target=_take_screenshot,
        args=(on_result, on_cancel, on_error),
    )
    thread.start()


def _take_screenshot(on_result, on_cancel, on_error):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join(app_screenshots_dir, f"screenshot_{timestamp}.png")
    command = ["maim", "-s", screenshot_path]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        return on_result(screenshot_path)
    except subprocess.CalledProcessError as err:
        cancel_pattern = re.compile(r"Selection was cancelled", re.IGNORECASE)
        if cancel_pattern.search(err.stderr):
            return on_cancel()
        raise
    except FileNotFoundError:
        msg = "'maim' command not found. Make sure it's installed and in your PATH."
        raise Exception(msg)
    except Exception as err:
        return on_error(err)
