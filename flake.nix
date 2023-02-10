{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

    flake-utils.url = "github:numtide/flake-utils";

    poetry2nix.url = "github:nix-community/poetry2nix";
    poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
    poetry2nix.inputs.flake-utils.follows = "flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix, ... }: flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = nixpkgs.legacyPackages.${system};
      p2n = poetry2nix.legacyPackages.${system};
      common = {
        projectDir = self;
      };
    in
    {
      packages = rec {
        yamlfmt = p2n.mkPoetryApplication common;
        default = yamlfmt;
      };

      devShells.default = (p2n.mkPoetryEnv common).env.overrideAttrs (prev: {
        buildInputs = [
          pkgs.python310
          pkgs.poetry
        ];
      });
    }
  );
}
