{inputs, ...}: {
  perSystem = {pkgs, ...}: let
    inherit (inputs) pyproject-nix;

    project = pyproject-nix.lib.project.loadPyproject {
      projectRoot = ./.;
    };

    python = pkgs.python3.override {
      packageOverrides = final: _prev: {
        pygobject = final.pygobject3;
      };
    };

    package = project.renderers.buildPythonPackage {
      inherit python;
    };

    override = {
      buildInputs = with pkgs; [
        gtk4
        libadwaita
        webkitgtk_6_0
      ];

      nativeBuildInputs = with pkgs; [
        wrapGAppsHook4
        gobject-introspection
      ];

      postInstall = ''
        mkdir -p $out/share/lean

        glib-compile-resources \
          --target=$out/share/lean/lean.gresource \
          --sourcedir=resources \
          resources/resources.xml

        install -D -t $out/share/glib-2.0/schemas ${./data/schemas/dev.vipulog.lean.gschema.xml}
        glib-compile-schemas $out/share/glib-2.0/schemas
      '';

      makeWrapperArgs = [
        "--set LEAN_RESOURCE_PATH $out/share/lean/lean.gresource"
      ];
    };

    app = python.pkgs.buildPythonApplication (
      package // override
    );
  in {
    packages = {
      lean = pkgs.symlinkJoin {
        name = "lean";
        paths = [app];
        nativeBuildInputs = [pkgs.makeWrapper];

        postBuild = ''
          wrapProgram $out/bin/lean \
            --prefix PATH : ${pkgs.lib.makeBinPath [pkgs.maim]} \
            --set GDK_BACKEND x11
        '';
      };
    };
  };
}
