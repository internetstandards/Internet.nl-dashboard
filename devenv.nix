{ pkgs, ... }:

let
  python = pkgs.python38;
in
{
  packages = [
    # development requirements
    pkgs.git
    pkgs.gnumake

    # Python version to use (see above)
    python

    # required for building MySQL Python package
    pkgs.libmysqlclient.dev
    # required for running dev environment
    pkgs.redis

    # additional tools
    pkgs.shellcheck
  ];

  env.DEBUG = 1;
  env.NETWORK_SUPPORTS_IPV6 = 1;
  env.PIP_DISABLE_PIP_VERSION_CHECK = 1;
  env.DJANGO_SETTINGS_MODULE = "websecmap.settings";

  enterShell = ''
    python_version=$(python --version)
    echo $python_version

    # enable debug by default
    DEBUG=1

    # pip should not complain about its version, mostly leads to red herrings
    export PIP_DISABLE_PIP_VERSION_CHECK=1

    # find a suitable place to create virtual environment outside of project directory
    if test "$(uname -s)" = "Darwin";then
        export VIRTUAL_ENV=~/Library/Caches/virtualenvs/$(basename $PWD)-''${python_version/\ /_}
    else
        export VIRTUAL_ENV=$\{XDG_CACHE_HOME:-~/.cache\}/virtualenvs/$(basename $PWD)-''${python_version/\ /_}
    fi
    echo "Virtualenv: $VIRTUAL_ENV"

    export PATH=$VIRTUAL_ENV/bin:$PATH

    # To the security researchers: these are placeholder keys that look like the real deal. The production environment
    # is simulated as well as possible. Please do not send any vulnerability disclosures about this. In many other
    # cases grepping through github works, this time it does not. Your efforts are appreciated still :)
    export SECRET_KEY="_dzlo^9d#ox6!7c9rju@=u8+4^sprqocy3s*l*ejc2yr34@&89"
    export FIELD_ENCRYPTION_KEY="_H1RMbPAgbhGHfG0Ok38OK6zNZ90P7AU9wULXp3aa1A="

    # This issue since catalina: https://gitlab.com/internet-cleanup-foundation/web-security-map/issues/229
    echo "Your system is running $OSTYPE."
    if [[ "$OSTYPE" == "darwin19" ]]; then
        export LDFLAGS=-L/usr/local/opt/openssl/lib
    fi

    export DJANGO_LOG_LEVEL=INFO
    export APP_LOG_LEVEL=DEBUG
    export CELERY_LOG_LEVEL=INFO
  '';

}

