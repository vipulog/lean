# shellcheck shell=bash

# ==============================================================================
# CONFIGURATION & GLOBAL STATE
# ==============================================================================
set -e # Exit on error
set -m # Enable job control

: "${XDG_STATE_HOME:=${HOME}/.local/state}"
APP_STATE_DIR="${XDG_STATE_HOME}/lean-session"

: "${XDG_DATA_HOME:=${HOME}/.local/share}"
APP_DATA_DIR="${XDG_DATA_HOME}/lean-session"

APP_LOG_DIR="${APP_STATE_DIR}/logs"
if [ -n "$APP_LOG_DIR" ] && [ "$APP_LOG_DIR" != "/" ]; then
  rm -rf "$APP_LOG_DIR"
  mkdir -p "$APP_LOG_DIR"
fi

# Global PIDs array for tracking background processes
declare -A PIDS
LOCK_FILE="${XDG_RUNTIME_DIR:-/tmp}/lean-session.lock"
TIMEOUT=10 # Seconds to wait for services to start

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

_log() {
  local level="$1"
  local color="$2"
  local msg="$3"
  local tag="${4:-}"

  local timestamp
  timestamp="$(date +"%F %T")"

  if [[ -n $tag ]]; then
    echo -e "${color}[${timestamp}] [${level}] [${tag}]${NC} $msg"
  else
    echo -e "${color}[${timestamp}] [${level}]${NC} $msg"
  fi
}

print_debug() {
  _log "DEBUG" "$NC" "$1" "${2:-}"
}

print_info() {
  _log "INFO" "$GREEN" "$1" "${2:-}"
}

print_warn() {
  _log "WARNING" "$YELLOW" "$1" "${2:-}"
}

print_error() {
  _log "ERROR" "$RED" "$1" "${2:-}"
}

wait_for() {
  local desc="$1"
  local check_cmd="$2"
  local count=0

  # Calculate how many loops equal the desired TIMEOUT (in seconds).
  # Since we sleep 0.2s, we need 5 loops per second.
  local max_attempts=$((TIMEOUT * 5))

  print_debug "Waiting for ${desc} (Max wait: ${TIMEOUT}s)..."

  while ! eval "$check_cmd"; do
    if [ "$count" -ge "$max_attempts" ]; then
      print_error "Timeout waiting for ${desc} after ${TIMEOUT} seconds"
      exit 1
    fi
    sleep 0.2
    count=$((count + 1))
  done
  print_debug "${desc} is ready."
}

cleanup() {
  local exit_code=$?
  print_debug "Starting cleanup (Exit Code: $exit_code)..."

  # Disable the trap to prevent infinite recursion if cleanup itself errors
  # or if we kill the script logic within this function.
  trap - EXIT INT TERM

  # Kill explicitly tracked background processes
  for service in "${!PIDS[@]}"; do
    local pid=${PIDS[$service]}
    if [[ -n $pid ]] && kill -0 "$pid" 2>/dev/null; then
      print_debug "Stopping $service (PID: $pid)..."
      kill -TERM "$pid" 2>/dev/null || true
    fi
  done

  # Kill the DBus session daemon (started via eval)
  if [[ -n $DBUS_SESSION_BUS_PID ]]; then
    print_debug "Stopping DBus Daemon (PID: $DBUS_SESSION_BUS_PID)..."
    kill "$DBUS_SESSION_BUS_PID" 2>/dev/null || true
  fi

  # Remove Lock File
  rm -f "$LOCK_FILE"

  # 'Nuclear' Option: Kill any remaining child jobs attached to this shell
  # Because set -m is on, we target jobs specifically rather than the process group.
  local remaining_jobs
  remaining_jobs=$(jobs -p)
  if [[ -n $remaining_jobs ]]; then
    print_debug "Killing remaining background jobs..."
    kill -TERM "$remaining_jobs" 2>/dev/null || true
  fi

  # Wait for processes to actually exit to prevent zombies
  print_debug "Waiting for processes to exit..."
  wait 2>/dev/null

  print_debug "Cleanup complete."
  exit "$exit_code"
}

# ==============================================================================
# MODULES
# ==============================================================================

check_lock() {
  if [ -e "$LOCK_FILE" ]; then
    LOCKED_PID=$(cat "$LOCK_FILE")
    if ps -p "$LOCKED_PID" >/dev/null; then
      print_error "Session already running (PID: ${LOCKED_PID})"
      exit 1
    else
      print_debug "Removing stale lock file."
      rm "$LOCK_FILE"
    fi
  fi
  echo $$ >"$LOCK_FILE"
}

setup_display_for_lean() {
  if [[ $XDG_SESSION_TYPE == "wayland" ]]; then
    print_debug "Host is Wayland. Initializing Xwayland..."

    # Create a named pipe (FIFO) to catch the display number
    local PIPE
    PIPE=$(mktemp -u)
    mkfifo "$PIPE"

    # Start Xwayland.
    # -displayfd 3: Write display number to FD 3
    # 3> "$PIPE": Redirect FD 3 to our named pipe
    Xwayland -geometry 1600x900 -displayfd 3 3>"$PIPE" >>"$APP_LOG_DIR/xwayland.log" 2>&1 &
    PIDS[xwayland]=$!

    # Read the display number (Blocking wait until Xwayland is ready)
    read -r DISPLAY_NUM <"$PIPE"
    rm "$PIPE"

    export DISPLAY=":${DISPLAY_NUM}"
    print_debug "Xwayland ready on ${DISPLAY}"

    # Start fluxbox
    print_debug "Starting fluxbox..."
    fluxbox >>"$APP_LOG_DIR/fluxbox.log" 2>&1 &
    PIDS[fluxbox]=$!
    sleep 1

  elif [[ $XDG_SESSION_TYPE == "x11" ]]; then
    print_debug "Host is X11. Using existing DISPLAY."
  else
    print_error "Unsupported session type: $XDG_SESSION_TYPE"
    exit 1
  fi
}

start_lean() {
  print_debug "Starting lean..."
  lean >>"$APP_LOG_DIR/lean.log" 2>&1 &
  PIDS[lean]=$!
}

setup_dbus() {
  print_debug "Setting up private DBus session..."

  # Export DBus variables to current shell immediately
  eval "$(dbus-launch --sh-syntax)"

  if [[ -z $DBUS_SESSION_BUS_ADDRESS ]]; then
    print_error "Failed to start DBus"
    exit 1
  fi
}

setup_screenshare() {
  print_debug "Setting up isolated screenshare stack..."

  if pgrep -x pipewire >/dev/null; then
    print_debug "pipewire already running (skipping start)"
  else
    print_debug "starting pipewire..."
    pipewire >>"$APP_LOG_DIR/pipewire.log" 2>&1 &
    PIDS[pipewire]=$!
  fi

  if pgrep -x wireplumber >/dev/null; then
    print_debug "wireplumber already running (skipping start)"
  else
    print_debug "starting wireplumber..."
    wireplumber >>"$APP_LOG_DIR/wireplumber.log" 2>&1 &
    PIDS[wireplumber]=$!
  fi

  wait_for "PipeWire Socket" "[ -e ${XDG_RUNTIME_DIR}/pipewire-0 ]"
}

setup_display_for_chromium() {
  export XDG_SESSION_TYPE=wayland
  export XDG_CURRENT_DESKTOP=sway
  unset WAYLAND_DISPLAY

  # Generate a temporary path for the ready file.
  local READY_FILE
  READY_FILE=$(mktemp -u)

  # Export it so sway knows where to write the success signal.
  export SWAY_DISPLAY_READY_FILE="$READY_FILE"

  print_debug "Starting sway..."
  sway >>"$APP_LOG_DIR/sway.log" 2>&1 &
  PIDS[sway]=$!

  # Wait for the file to exist AND have content.
  wait_for "sway" "[ -s '$READY_FILE' ]"

  # Read the display value (e.g., "wayland-1")
  local NEW_DISPLAY
  NEW_DISPLAY=$(cat "$READY_FILE")

  # Set global environment for future processes (Portals, Chromium)
  export WAYLAND_DISPLAY="$NEW_DISPLAY"
  print_debug "sway ready. Attached to WAYLAND_DISPLAY=${WAYLAND_DISPLAY}"

  # Clean up the temp file
  rm -f "$READY_FILE"
}

setup_portals() {
  print_debug "Starting Portals..."
  export XDG_DESKTOP_PORTAL_DIR="$LEAN_XDG_DESKTOP_PORTAL_CONF_DIR"

  "$LEAN_XDG_DESKTOP_PORTAL_WLR_BIN" >>"$APP_LOG_DIR/portal-wlr.log" 2>&1 &
  PIDS[portal_backend]=$!

  # Wait briefly for backend to register on DBus
  # (Portals are notoriously race-prone, a short sleep here is sometimes unavoidable
  # unless you query DBus for the service name org.freedesktop.impl.portal.desktop.wlr)
  wait_for "Portal Backend DBus Name" "busctl --user list | grep -q 'portal.desktop.wlr'"

  "$LEAN_XDG_DESKTOP_PORTAL_BIN" >>"$APP_LOG_DIR/portal.log" 2>&1 &
  PIDS[portal]=$!
}

start_chromium() {
  print_debug "Starting Chromium..."
  chromium \
    --user-data-dir="${APP_DATA_DIR}/chromium/" \
    --no-first-run \
    --ozone-platform=wayland \
    >>"$APP_LOG_DIR/chromium.log" 2>&1 &
  PIDS[chromium]=$!
}

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

trap cleanup EXIT INT TERM

check_lock
setup_display_for_lean
start_lean
setup_dbus
setup_screenshare
setup_display_for_chromium
setup_portals
start_chromium

print_debug "Session initialized successfully."
print_debug "Waiting for main processes (Lean or Xwayland) to exit..."

wait "${PIDS[lean]}"

print_debug "Main process exited."
