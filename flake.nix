{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
        let
        pkgs = import nixpkgs {
            system = system;
        }; in {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
              # development requirements
              python310
              git
              gnumake
              bash
              pcre2
              yajl
              libxml2
              libxcrypt

              uv

              # required for building MySQL Python package
              libmysqlclient.dev
              postgresql

              # required for running dev environment
              redis

              # libmagic
              file

              # additional tools
              shellcheck
              basedpyright

              docker-compose
          ];
          env = {
              DEBUG = 1;
              NETWORK_SUPPORTS_IPV6 = 1;
              PIP_DISABLE_PIP_VERSION_CHECK = 1;
              DJANGO_SETTINGS_MODULE = "dashboard.settings";
              MYSQLCLIENT_CFLAGS = "-I${pkgs.libmysqlclient.dev}/include/mysql";
              MYSQLCLIENT_LDFLAGS = "-L${pkgs.libmysqlclient.dev}/lib";
              PROJECT_WEBSITE = "http://localhost:8000";
              LD_LIBRARY_PATH= "${pkgs.stdenv.cc.cc.lib}/lib/";
              # make libmagic findable for Python packages in venv
              DYLD_LIBRARY_PATH="${pkgs.file}/lib";
              # somehow the pylama warning can't be silenced from pyproject.tojml [tool.pytest.ini_options]
              PYTHONWARNINGS=''
                  error::RuntimeWarning,
                  ignore::UserWarning:pylama.lint,
                  ignore::UserWarning:google
              '';
          };
          shellHook = ''
            # do this in a shellhook as $PWD is not available in `env =` above due to Nix purity
            export VIRTUAL_ENV="$PWD/.venv";
            echo "Virtualenv: $VIRTUAL_ENV"
            export PATH=$VIRTUAL_ENV/bin:$PATH
          # '';
        };
    });
}
