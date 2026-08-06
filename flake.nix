{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
        let
        pkgs = import nixpkgs {
            system = system;
        };
        docsTexlive = pkgs.texlive.combine {
            inherit (pkgs.texlive)
                scheme-small
                latexmk
                xetex
                luatex
                luatex85
                luaotfload
                fontspec
                polyglossia
                babel-english
                hyphen-english
                cmap
                amsmath
                geometry
                hyperref
                hypcap
                bookmark
                graphics
                graphics-cfg
                graphics-def
                float
                colortbl
                booktabs
                fncychap
                zapfchan
                tocloft
                capt-of
                pict2e
                ellipse
                needspace
                tabulary
                varwidth
                framed
                fancyvrb
                fvextra
                upquote
                wrapfig
                parskip
                titlesec
                etoolbox
                fancyhdr
                pdftexcmds
                kvoptions
                oberdiek
                makeindex
            ;
        };
        in {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
              # development requirements
              python313
              git
              gnumake
              bash
              pcre2
              yajl
              libxml2
              libxcrypt

              uv
              docsTexlive
              dejavu_fonts
              liberation_ttf
              noto-fonts-emoji

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
              OSFONTDIR = "${pkgs.dejavu_fonts}/share/fonts/truetype:${pkgs.liberation_ttf}/share/fonts/truetype:${pkgs.noto-fonts-emoji}/share/fonts/noto";
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
