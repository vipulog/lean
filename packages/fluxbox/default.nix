{
  perSystem = {pkgs, ...}: let
    rcFile = import ./rc.nix {inherit pkgs;};
  in {
    packages.fluxbox = pkgs.symlinkJoin {
      name = "fluxbox";
      paths = [pkgs.fluxbox];
      nativeBuildInputs = [pkgs.makeWrapper];

      postBuild = ''
        wrapProgram $out/bin/fluxbox \
          --add-flags "-no-toolbar" \
          --add-flags "-rc ${rcFile}"
      '';
    };
  };
}
