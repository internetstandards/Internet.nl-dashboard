# dashboard-internet.nl

[![Badges](https://img.shields.io/badge/badges-1-yellowgreen.svg)](https://shields.io)

These instructions will help you set up a development version of the dashboard.

Getting started
===============
Keywords: quickstart, installation


## 1: Install dependencies on your system
Setup your system to run this software using your favourite package manager.

**MacOS (brew)**
```bash
brew install git python3 direnv
```

**Debian Linux (apt)**
```bash
apt-get install git python3 direnv
```

**Redhat/CentOS (yum)**
```bash
yum install git python3 direnv
```

Or download and install each package separately:

- [make](https://www.gnu.org/software/make/) (required, pre-installed on most systems)
- [git](https://git-scm.com/downloads) (required, download and install)
- [python3](https://www.python.org/downloads/) (required, download and install, 3.8 or higher)
- [direnv](https://direnv.net/) (recommended, download and install, then follow [setup instructions](https://direnv.net/), see Direnv section below)
- [Docker](https://docs.docker.com/engine/installation/) (recommended, follow instructions to install.)
- [ShellCheck](https://github.com/koalaman/shellcheck#installing) (recommended, follow instructions to install

## 2: Install direnv correctly
Then set up direnv, the right command depends on your shell:

**BASH**
Add the following line at the end of the ~/.bashrc file:
```bash
eval "$(direnv hook bash)"
```

Make sure it appears even after rvm, git-prompt and other shell extensions that manipulate the prompt.

**ZSH**
Add the following line at the end of the ~/.zshrc file:
```bash
eval "$(direnv hook zsh)"
```

**FISH**
Add the following line at the end of the ~/.config/fish/config.fish file:

```bash
eval (direnv hook fish)
```

**TCSH**
Add the following line at the end of the ~/.cshrc file:

```bash
eval `direnv hook tcsh`
```


## 3: Generic install steps

In a directory of your choosing, download the software and enter the directory:

```bash
git clone --recursive https://https://github.com/internetstandards/Internet.nl-dashboard && cd Internet.nl-dashboard/
```

Running `make` once to create a development Virtualenv and setup the App and its dependencies. Running `make` without arguments by default also runs basic checks and tests to verify project code quality.

```bash
make
```

After completing successfully Web Security Map development server is available to run:

```bash
make run
```

If you want to run the frontend, or a worker, or the broker, run:

```bash
make run-frontend
```

Now visit the [website](http://127.0.0.1:8000/) and/or the
[admin website](http://127.0.0.1:8000/admin/) at http://127.0.0.1:8000 (credentials: dashboard_admin:admin).


To prepare the shell environment for local development. This way you can run the 'dashboard' command.

```bash
direnv allow
```

After completing successfully Dashboard is available to run. For example, to show a list of commands:

```bash
dashboard help
```

To create your first user:

```bash
dashboard createsuperuser
```

Development:
```
dashboard migrate
dashboard loaddata dashboard_development.json
```



#### Optional Steps

If your shell support tab completion you can get a complete list of supported commands by tabbing `make`:

```bash
make <tab><tab>
```

## 4: Common tasks

### Update dependencies/requirements

Python dependencies are managed using [pip-tools](https://github.com/jazzband/pip-tools). See `requirements.in` and `requirements-dev.in`.

For convenience the following command can be used to update all Python dependencies (within their version boundaries):

    make update_requirements

The dependency on Web Security Map is version pinned by a Git SHA in the Websecmap Gitlab repo. The following command will lookup the SHA for the current master in Gitlab, update the `requirements.in` file, update the dependencies, and even commit everything to Git.

    make update_requirement_websecmap

## FAQ / Troubleshooting

### Missing xcode (mac users)
During installation mac users might get the following error, due to not having xcode installed or updated.

```
xcrun: error: invalid active developer path (/Library/Developer/CommandLineTools), missing xcrun at: /Library/Developer/CommandLineTools/usr/bin/xcrun
```

You can update / install xcode tools with the following command:

```
xcode-select --install
```

### Missing Docker Daemon (mac users)
While docker is installed using brew in prior steps, you probably want to have
a gui controlling docker.

Docker for mac can be downloaded here:
https://download.docker.com/mac/stable/Docker.dmg

You can also visit the docker website and get the link using the time tested Oracle(tm) download strategy, here:
https://hub.docker.com/editions/community/docker-ce-desktop-mac


### Missing zstd or other stuff from LD

`brew install zstd`
`which zstd`
`set -x LDFLAGS -L/opt/homebrew/bin/zstd`
`set -x LDFLAGS -L/opt/homebrew/lib/ -L/opt/homebrew/openssl/lib`


### Cannot compile psycopg2 on m1 mac:
https://stackoverflow.com/questions/66888087/cannot-install-psycopg2-with-pip3-on-m1-mac
TLDR, run below commands and try again:
```json
export LDFLAGS="-L/opt/homebrew/opt/openssl@1.1/lib -L/opt/homebrew/opt/libpq/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl@1.1/include -I/opt/homebrew/opt/libpq/include"
```


### Missing lib magic on mac:
Where you need the x86 version, because this library is x86 only due cffi not supporting m1:
`arch -x86_64 /usr/local/bin/brew install libmagic`

Because libmagic supresses loading errors, you'll only find out that the wrong binary is
getting loaded when adding print statements there. If the library doesn't load it's probably because:

```shell
/opt/local/lib/libmagic.dylib
dlopen(/opt/local/lib/libmagic.dylib, 6): image not found
/usr/local/lib/libmagic.dylib
dlopen(/usr/local/lib/libmagic.dylib, 6): image not found
/opt/homebrew/lib/libmagic.dylib
dlopen(/opt/homebrew/lib/libmagic.dylib, 6): no suitable image found.  Did find:
	/opt/homebrew/lib/libmagic.dylib: mach-o, but wrong architecture
	/opt/homebrew/Cellar/libmagic/5.41/lib/libmagic.1.dylib: mach-o, but wrong architecture
```

So you should install the Intel binary for this version.

You can use the alternative brew installation in /usr/local/bin
and run: `arch -x86_64 sh`, `cd /usr/local/bin`, `/brew install --build-from-source libmagic`

and run: `arch -x86_64 brew install libmagic`
You'll get an error but at least there is now an x64/intel file at: `/usr/local/lib/libmagic.dylib`
