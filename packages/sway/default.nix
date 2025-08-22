{
  perSystem = {pkgs, ...}: let
    configFile = import ./config.nix {inherit pkgs;};
  in {
    packages.sway = pkgs.symlinkJoin {
      name = "sway";
      paths = [pkgs.sway];
      nativeBuildInputs = [pkgs.makeWrapper];

      postBuild = ''
        wrapProgram $out/bin/sway \
          --set WLR_BACKENDS x11 \
          --set WLR_LIBINPUT_NO_DEVICES 1 \
          --add-flags "--config ${configFile}"
      '';
    };
  };
}
