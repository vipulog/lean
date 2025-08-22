import os

app_cache_dir = os.environ.get(
    "XDG_CACHE_HOME/lean",
    os.path.join(os.path.expanduser("~"), ".cache/lean"),
)
os.makedirs(app_cache_dir, exist_ok=True)

app_state_dir = os.environ.get(
    "XDG_STATE_HOME/lean",
    os.path.join(os.path.expanduser("~"), ".local/state/lean"),
)
os.makedirs(app_state_dir, exist_ok=True)

app_logs_dir = os.path.join(app_state_dir, "logs")
os.makedirs(app_logs_dir, exist_ok=True)

app_screenshots_dir = os.path.join(app_cache_dir, "screenshots")
os.makedirs(app_screenshots_dir, exist_ok=True)
