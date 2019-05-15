# configure virtualenv to be created in OS specific cache directory
ifeq ($(UNAME_S),Darwin)
# macOS cache location
CACHEDIR ?= ~/Library/Caches
else
# User customized cache location or Linux default
XDG_CACHE_HOME ?= ~/.cache
CACHEDIR ?= ${XDG_CACHE_HOME}
endif
VIRTUAL_ENV ?= ${CACHEDIR}/virtualenvs/$(notdir ${PWD})
$(info Virtualenv path: ${VIRTUAL_ENV})

$(info )


# shortcuts for common used binaries
bin = ${VIRTUAL_ENV}/bin
env = PATH=${bin}:$$PATH
python = ${bin}/python
pip = ${bin}/pip
poetry = ${bin}/poetry

# application binary
app_name = dashboard
app = ${bin}/${app_name}

commands = devserver

pysrcdirs = ${app_name}/ tests/
pysrc = $(shell find ${pysrcdirs} -name *.py)
shsrc = $(shell find * .github ! -path vendor\* -name *.sh)

.PHONY: ${commands} test check setup run fix autofix clean mrproper poetry test_integration

# default action to run
all: check test

# setup entire dev environment
setup: | ${app}

# install application and all its (python) dependencies
${app}: poetry.lock | poetry
	# install project and its dependencies
	VIRTUAL_ENV=${VIRTUAL_ENV} ${poetry} install --develop=$(notdir ${app}) ${poetry_args}
	test -f $@ && touch $@

test: .make.test
.make.test: ${pysrc} | setup
	# run testsuite
	DJANGO_SETTINGS_MODULE=${app_name}.settings ${env} coverage run --include '${app_name}/*' \
		-m pytest -k 'not integration and not system' ${testargs}
	# generate coverage
	${env} coverage report
	# and pretty html
	${env} coverage html
	# ensure no model updates are commited without migrations
	${app} makemigrations --check
	@touch $@

check: .make.check
.make.check: ${pysrc} ${shsrc} | setup
	# check code quality
	${env} pylama ${pysrcdirs} --skip "**/migrations/*"
	@touch $@

autofix fix: .make.fix
.make.fix: ${pysrc} | setup
	# fix trivial pep8 style issues
	${env} autopep8 -ri ${pysrcdirs}
	# remove unused imports
	${env} autoflake -ri --remove-all-unused-imports ${pysrcdirs}
	# sort imports
	${env} isort -rc ${pysrcdirs}
	# do a check after autofixing to show remaining problems
	${MAKE} check
	@touch $@

run: | setup
	# start server (this can take a while)
	DEBUG=1 NETWORK_SUPPORTS_IPV6=1 ${app} devserver

test_integration: | setup
  	DB_NAME=test.sqlite3 ${run} pytest -v -k 'integration' ${testargs}

${commands}: | setup
	${app} $@ ${args}

test_integration: | setup
	# run integration tests
	${env} DJANGO_SETTINGS_MODULE=${app_name}.settings DB_NAME=test.sqlite3 \
	${env} pytest -k 'integration' ${testargs}

test_system:
	# run system tests
	${env} pytest tests/system ${testargs}

test_image:
	docker-compose up

# cleanup build artifacts, caches, etc.
clean:
	# remove python cache files
	-find * -name __pycache__ -print0 | xargs -0 rm -rf
	# remove state files
	-rm -f .make.*
	# remove test artifacts
	-rm -rf .pytest_cache htmlcov/
	# remove build artifacts
	-rm -rf *.egg-info dist/ pip-wheel-metadata/
	# remove runtime state files
	-rm -rf *.sqlite3

# thorough clean, remove virtualenv
mrproper: clean
	-rm -fr ${VIRTUAL_ENV}/

# don't let poetry manage the virtualenv, we do it ourselves to make it deterministic
poetry: ${poetry}
poetry_version=0.12.15
${poetry}: ${python}
	# install poetry
	${pip} install -q poetry==${poetry_version}

${python}:
	@if ! command -v python3 &>/dev/null;then \
		echo "Python 3 is not available. Please refer to installation instructions in README.md"; \
	fi
	# create virtualenv
	python3 -mvenv ${VIRTUAL_ENV}
