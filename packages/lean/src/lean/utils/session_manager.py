import json
import os
from datetime import datetime

from .logs import dump_error
from .paths import app_logs_dir


class SessionManager:
    def __init__(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_path = os.path.join(app_logs_dir, f"session_{timestamp}.log")

    def update_and_log(self, image_path, input_tokens, output_tokens):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "image_path": image_path,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }

        try:
            with open(self.log_file_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as err:
            dump_error(err)
