{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in with pkgs;
      {
        devShells.default =
          mkShell {
            buildInputs = with python312Packages; [
                coverage
                z3
                setuptools
                openai
                python-dotenv
                matplotlib
            ] ++ [
                uv
            ];
          };
      }
    );
}
