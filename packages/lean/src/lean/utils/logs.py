import os
import traceback
from datetime import datetime

from .paths import app_logs_dir


def dump_error(err):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    err_log_path = os.path.join(app_logs_dir, f"error_{timestamp}.log")
    with open(err_log_path, "w") as f:
        f.write(f"Error: {str(err)}\n")
        f.write("Traceback:\n")
        f.write(traceback.format_exc())
    return err_log_path
