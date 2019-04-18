# dashboard-internet.nl
Dashboard Internet.nl

[![Actions Status](https://wdp9fww0r9.execute-api.us-west-2.amazonaws.com/production/badge/aequitas/Internet.nl-dashboard)](https://wdp9fww0r9.execute-api.us-west-2.amazonaws.com/production/results/aequitas/Internet.nl-dashboard)


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

- [git](https://git-scm.com/downloads) (download and install)
- [python3.6](https://www.python.org/downloads/) (download and install)
- [Tox](http://tox.readthedocs.io/) (`pip3 install --user tox`)
- [direnv](https://direnv.net/) (download and install, then follow [setup instructions](https://direnv.net/), see Direnv section below)

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
Install Tox, which helps to install the rest of the dependencies of this project:

```bash
pip3 install --user tox
```

In a directory of your choosing:

download the software

```bash
git clone --recursive https://https://github.com/internetstandards/Internet.nl-dashboard
```

enter the directory of the downloaded software

```bash
cd Internet.nl-dashboard/
```

This prepares the shell environment for local development.

```bash
direnv allow
```

Running Tox once creates a development Virtualenv in .tox/default/ which is automatically used after creation due to Direnv setup. Running Tox without arguments by default also runs basic checks and tests to verify project code quality.

```bash
tox
```

After completing successfully Dashboard is available to run. For example, to show a list of commands:

```bash
dashboard help
```

To create your first user:

```bash
dashboard createsuperuser
```

Now run the following command to start a full development server.

```bash
dashboard runserver
```
