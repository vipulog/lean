{
  perSystem = {
    pkgs,
    self',
    ...
  }: {
    packages.lean-session = pkgs.writeShellApplication {
      name = "lean-session";
      text = builtins.readFile ./main.sh;

      runtimeInputs = with pkgs; [
        self'.packages.lean
        self'.packages.fluxbox
        self'.packages.sway
        pipewire
        wireplumber
        xwayland
        xclip
        wl-clipboard
        chromium
      ];

      runtimeEnv = {
        LEAN_XDG_DESKTOP_PORTAL_BIN = "${pkgs.xdg-desktop-portal}/libexec/xdg-desktop-portal";
        LEAN_XDG_DESKTOP_PORTAL_WLR_BIN = "${pkgs.xdg-desktop-portal-wlr}/libexec/xdg-desktop-portal-wlr";
        LEAN_XDG_DESKTOP_PORTAL_CONF_DIR = "${pkgs.xdg-desktop-portal-wlr}/share/xdg-desktop-portal/portals";
      };
    };

    apps.default = {
      type = "app";
      program = "${self'.packages.lean-session}/bin/lean-session";
    };
  };
}
