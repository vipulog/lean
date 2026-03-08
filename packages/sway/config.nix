{pkgs, ...}:
pkgs.writeText "config" ''
  # Variables
  set $mod Mod4

  # Basic settings
  default_border none
  default_floating_border none
  gaps inner 0
  gaps outer 0

  # Disable all window decorations
  titlebar_border_thickness 0
  titlebar_padding 0

  # Output configuration
  output * {
    bg #000000 solid_color
    scale 1
  }

  # Input configuration
  input "type:keyboard" {
    xkb_layout us
  }

  input "type:touchpad" {
    tap enabled
  }

  xwayland disable

  for_window [app_id=".*"] floating enable
  for_window [app_id="chromium"] floating disable

  seat seat0 hide_cursor 1000

  exec echo "$WAYLAND_DISPLAY" > "''${SWAY_DISPLAY_READY_FILE:-/tmp/sway-display-ready}"
''
