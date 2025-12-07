{
  description = "PartSuite 2.0 - Django/DRF dev environment";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-23.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          django
          djangorestframework
          django-filter
          django-environ
          pypdf
          drf-spectacular
          celery
          redis
          psycopg2
          python-dotenv
          uvicorn
          gunicorn
        ]);
      in {
        devShells.default = pkgs.mkShell {
          packages = [
            pythonEnv
            pkgs.postgresql
            pkgs.redis
            pkgs.minio-client
            pkgs.tesseract
            pkgs.poppler_utils
            pkgs.imagemagick
          ];

          shellHook = ''
            export DJANGO_SETTINGS_MODULE=partsuite.settings
            echo "Dev shell ready. Python: $(python --version)"
          '';
        };
      });
}
