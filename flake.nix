{
  outputs = inputs @ {flake-parts, ...}: (
    flake-parts.lib.mkFlake {
      inherit inputs;
      specialArgs = {rootPath = ./.;};
    } {
      systems = ["x86_64-linux" "aarch64-linux"];
      imports = [./flake-parts.nix];
    }
  );

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";

    git-hooks-nix = {
      url = "github:cachix/git-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
}
