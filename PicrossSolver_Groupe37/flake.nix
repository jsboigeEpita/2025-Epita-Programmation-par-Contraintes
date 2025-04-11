{
  inputs = {
    utils.url = "github:numtide/flake-utils";
  };
  outputs = {
    self,
    nixpkgs,
    utils,
  }:
    utils.lib.eachDefaultSystem (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            lolcat
            (python312.withPackages (ppkgs:
              with ppkgs; [
                pillow
                numpy
                ortools
                pandas
              ]))
          ];
        };
      }
    );
}
