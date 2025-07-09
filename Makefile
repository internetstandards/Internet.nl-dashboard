SHELL=/bin/bash

# settings
app_name = dashboard
docker_image_name = internetstandards/dashboard

# configure virtualenv to be created in OS specific cache directory
ifeq ($(shell uname -s),Darwin)
# macOS cache location
CACHEDIR ?= ~/Library/Caches
else
# User customized cache location or Linux default
XDG_CACHE_HOME ?= ~/.cache
CACHEDIR ?= ${XDG_CACHE_HOME}
endif
VIRTUAL_ENV ?= ${CACHEDIR}/virtualenvs/$(notdir ${PWD})
$(info Virtualenv path: ${VIRTUAL_ENV})

# variables for environment
bin = ${VIRTUAL_ENV}/bin
env = PATH=${bin}:$$PATH

# shortcuts for common used binaries
uv = uv # provided by flake.nix
python = ${bin}/python3.10
python3 = ${bin}/python3.10
pip = ${bin}/pip
pip-compile = ${bin}/pip-compile
pip-sync = ${bin}/pip-sync

# application binary
app = ${bin}/${app_name}

$(shell test -z "$$PS1" || echo -e \nRun `make help` for available commands or use tab-completion.\n)

pysrcdirs = ${app_name}/
pysrc = $(shell find ${pysrcdirs} -name \*.py 2>/dev/null)
src = $(shell find ${pysrcdirs} -type f -print0 2>/dev/null)
shsrc = $(shell find * ! -path vendor\* -name \*.sh 2>/dev/null)

.PHONY: test check pylama pylint shellcheck setup run fix autofix clean mrproper test_integration requirements requirements-dev docs

# default action to run
all: check test setup requirements

## Setup
# setup entire dev environment
setup: ${app}	## setup development environment and application
	@test \! -z "$$PS1" || (echo -ne "Development environment is tested and ready."; \
	if command -v dashboard &>/dev/null;then \
		echo -e " Development shell is activated."; \
	else \
		echo -e "\n\nTo activate development shell run:"; \
		echo -e "\n\t. ${VIRTUAL_ENV}/bin/activate$$([[ "$$SHELL" =~ "fish" ]] && echo .fish)\n"; \
		echo -e "Or refer to Direnv in README.md for automatic activation."; \
	fi)

# install application and all its (python) dependencies
${app}: ${VIRTUAL_ENV}/.requirements.installed | ${uv}
	# install project and its dependencies
	uv pip install --no-deps --editable .
	@test -f $@ && touch $@  # update timestamp, do not create empty file


${VIRTUAL_ENV}/.requirements.installed: requirements.txt requirements-dev.txt | ${uv} ${python}
	uv pip sync $^
	@touch $@  # update timestamp

# perform 'pip freeze' on first class requirements in .in files.
requirements: requirements.txt requirements-dev.txt requirements-deploy.txt
# perform 'pip freeze' on first class requirements in .in files.
requirements.txt: requirements.in | ${uv}
	${uv} pip compile ${pip_compile_args} --custom-compile-command="make requirements" --no-strip-extras --output-file $@ $<

requirements-dev.txt: requirements-dev.in requirements.in | ${uv}
	${uv} pip compile ${pip_compile_args} --custom-compile-command="make requirements" --no-strip-extras --output-file $@ $<

pip-sync: | ${python}
	# synchronizes the .venv with the state of requirements.txt
	${uv} pip sync requirements.txt requirements-dev.txt


upgrade_package: | ${uv} ## upgrade a single Python package in requirements.txt
	@if [ -z "${package}" ];then echo "Usage: make upgrade_package package=package-name"; exit 1; fi
	${uv} pip compile requirements.in --upgrade-package ${package} > requirements.txt

upgrade_dev_package: | ${uv} ## upgrade a single Python package in requirments-dev.txt
	@if [ -z "${package}" ];then echo "Usage: make upgrade_dev_package package=package-name"; exit 1; fi
	${uv} pip compile requirements-dev.in --upgrade-package ${package} > requirements-dev.txt


update_requirements: pip_compile_args=--upgrade --resolver=backtracking
update_requirements: _mark_outdated requirements.txt requirements-dev.txt requirements-deploy.txt _commit_update

_mark_outdated:
	touch requirements*.in

# get latest sha for gitlab.com:icf/websecmap@master and update requirements
update_requirement_websecmap: _update_websecmap_sha requirements.txt _commit_update

_update_websecmap_sha:
	sha=$(shell git ls-remote -q git@gitlab.com:internet-cleanup-foundation/web-security-map.git master|cut -f1); \
	if grep $$sha requirements.in >/dev/null; then echo -e "\nNo update for you, current sha for websecmap in requirements.in is the same as master on Gitlab.\n"; exit 1;fi; \
	sed -E -i '' "s/web-security-map@[a-zA-Z0-9]{40}/web-security-map@$$sha/" requirements.in requirements-deploy.in

_commit_update: requirements.txt
	git add requirements*.txt requirements*.in
	git commit -m "Updated requirements."

## Environment requirements
environment_dependencies: libmagic

# Note that there is no wheel for pillow on python3.8 on mac, wheels start at python 3.9. Use 3.9
ifeq ($(shell uname -s),Darwin)
brew_prefix = $(shell brew --prefix)
brew = ${brew_prefix}/bin/brew

libmagic: ${brew_prefix}/Cellar/libmagic/
${brew_prefix}/Cellar/libmagic/: | ${brew}
	brew install libmagic

${brew}:
	@echo "Please install homebrew: https://brew.sh"
	false
else
libmagic: /usr/lib/x86_64-linux-gnu/libmagic.so.1
/usr/lib/x86_64-linux-gnu/libmagic.so.1:
	apt install -yqq libmagic1
endif

## QA
tests = .
test: ${src} ${app}
	# run testsuite
	DJANGO_SETTINGS_MODULE=${app_name}.settings ${env} coverage run --include '${app_name}/*' --omit '*migrations*' \
		-m pytest --no-migrations -k 'not integration and not system and ${tests}' ${testargs}
	# generate coverage
	${env} coverage report
	# and pretty html
	${env} coverage html
	# ensure no model updates are commited without migrations
	${env} ${app} makemigrations --verbosity=3 --check ${app_name}

check: pylama shellcheck pylint ## code quality checks
pylama: ${pysrc} ${app}
	# check code quality
	${env} pylama ${pysrcdirs} --skip "**/migrations/*"


shellcheck: ${shsrc}
	# shell script checks (if installed)
	if command -v shellcheck &>/dev/null && ! test -z "${shsrc}";then ${env} shellcheck ${shsrc}; fi

autofix fix: ${pysrc} ${app} ## automatic fix of trivial code quality issues
	# fix trivial pep8 style issues
	${env} autopep8 -ri ${pysrcdirs}
	# remove unused imports
	${env} autoflake -ri --remove-all-unused-imports ${pysrcdirs}
	# sort imports
	${env} isort -rc ${pysrcdirs}
	black .
	# do a check after autofixing to show remaining problems
	${MAKE} check

## Running
# run: ${app}  ## run complete application stack (frontend, worker, broker)
# 	# start server (this can take a while)
# 	DEBUG=1 NETWORK_SUPPORTS_IPV6=1 ${env} ${app} devserver

run-frontend: ${app}  ## only run frontend component
	DEBUG=1 NETWORK_SUPPORTS_IPV6=1 ${env} ${app} runserver

run-gui-development build-gui-staging build-gui-production:
	build-gui-production; $(MAKE) $@

app: ${app}  ## perform arbitrary app commands
	## For example: make app cmd=migrate
	# make app cmd="loaddata development"
	# make app cmd="help"
	# make app cmd="report -y municipality"
	# make app cmd="makemigrations"
	# make app cmd="migrate"
	DEBUG=1 NETWORK_SUPPORTS_IPV6=1 ${env} ${app} ${cmd}

run-worker: ${app}  ## only run worker component
	DEBUG=1 NETWORK_SUPPORTS_IPV6=1 ${env} ${app} celery worker -ldebug -Q storage,celery,reporting,ipv4,ipv6,4and6,internet,isolated,database,kickoff,default,database_deprecate

run-broker:  ## only run broker
	docker run --rm --name=redis -p 6379:6379 redis

## Testing
test_integration: ${app}  ## perform integration test suite
	DB_NAME=test.sqlite3 ${env} pytest -vv -k 'integration' ${testargs}

test_datasets: ${app}
	${env} /bin/sh -ec "find ${app_name}/ -path '*/fixtures/*.yaml' -print0 | \
		xargs -0n1 basename -s .yaml | uniq | \
		xargs -n1 ${app} test_dataset"

test_deterministic: | ${VIRTUAL_ENV}
	${env} /bin/bash tools/compare_differences.sh HEAD HEAD tools/show_ratings.sh testdata

pull_image:
	# optimize build by caching previously build image
	-docker pull ${docker_image_name}

push_image:
	docker push ${docker_image_name}

image:  ## Create Docker images
	docker build -t ${docker_image_name} ${build_args} .

docs: ## Generate documentation in various formats
	# Remove existing documentation folder
	-rm -rf docs/render/*
	${python} -m sphinx -b html docs/input docs/render/html
	${python} -m sphinx -b markdown docs/input docs/render/markdown
	${python} -m sphinx -b pdf docs/input docs/render/pdf

## Housekeeping
clean:  ## cleanup build artifacts, caches, databases, etc.
	# remove python cache files
	-find * -name __pycache__ -print0 | xargs -0 rm -rf
	# remove test artifacts
	-rm -rf .pytest_cache htmlcov/
	# remove build artifacts
	-rm -rf *.egg-info dist/ pip-wheel-metadata/
	# remove runtime state files
	# -rm -rf *.sqlite3

clean_virtualenv:  ## cleanup virtualenv and installed app/dependencies
	# remove virtualenv
	-rm -fr ${VIRTUAL_ENV}

mrproper: clean clean_virtualenv ## thorough cleanup, also removes virtualenv

run-autoreload-browser: run
run-autoreload-browser: autoreload_browser=1

autoreload_browser ?=


## Base requirements

${python} ${VIRTUAL_ENV}:
	# create virtualenv, Python version is determined by pyproject.toml requires-python
	${uv} venv

${uv}:

# work around not having nix flake with uv in build.
python: ${python}
${python} ${uv}:
	@if ! command -v python3 &>/dev/null;then \
		echo "Python 3 is not available. Please refer to installation instructions in README.md"; \
	fi
	# create virtualenv
	python3.10 -mvenv ${VIRTUAL_ENV}
	# ensure a recent version of pip is used to avoid errors with installing
	${VIRTUAL_ENV}/bin/pip install --upgrade "uv"

mypy: ${app} ## Check for type issues with mypy
	${python} -m mypy --check dashboard

vulture: ${app} ## Check for unused code
	${python} -m vulture ${pysrcdirs}

ruff: ${app} ## Faster than black, might autoformat some things
	${python} -m ruff check ${pysrcdirs}

bandit: ${app} ## Run basic security audit
	${python} -m bandit --configfile bandit.yaml -r ${pysrcdirs}

pylint: ${app}
	DJANGO_SETTINGS_MODULE=${app_name}.settings ${bin}/pylint --load-plugins pylint_django dashboard

.QA: qa
qa: fix pylint bandit vulture check test ruff


## Utility
help:           ## Show this help.
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "\nRun \`make\` with any of the targets below to reach the desired target state.\n" ; \
	printf "\nTargets are complementary. Eg: the \`run\` target requires \`setup\` which is automatically executed.\n\n" ; \
	printf "%-30s %s\n" "target" "help" ; \
	printf "%-30s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-30s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done
