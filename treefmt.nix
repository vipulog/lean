{inputs, ...}: {
  imports = [inputs.treefmt-nix.flakeModule];

  perSystem = {
    treefmt = {
      programs = {
        alejandra.enable = true;
        deadnix.enable = true;
        shellcheck.enable = true;
        shfmt.enable = true;
        ruff-check.enable = true;
        ruff-format.enable = true;
        prettier = {
          enable = true;
          excludes = ["*.min.js"];
        };
      };

      settings.formatter = {
        deadnix.no_lambda_arg = true;
        shellcheck.options = ["-x" "-P" "packages/lean-session/src"];
      };
    };
  };
}
