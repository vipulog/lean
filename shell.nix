{
  perSystem = {
    pkgs,
    config,
    ...
  }: {
    devShells.default = pkgs.mkShell {
      inputsFrom = [
        config.pre-commit.devShell
        config.treefmt.build.devShell
      ];
    };
  };
}
