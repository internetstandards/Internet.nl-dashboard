all: check test

VIRTUAL_ENV = $(shell poetry config settings.virtualenvs.path|tr -d \")/dashboard-py3.6
run := poetry run

setup: | ${VIRTUAL_ENV}/bin/dashboard

${VIRTUAL_ENV}/bin/dashboard: | poetry
	poetry run pip install --upgrade pip==19.1.1
	poetry install
	@test -f $@ && touch $@

poetry: .installed.poetry
.installed.poetry:
	if ! command -v poetry >/dev/null; then \
		pip install --upgrade poetry=0.12.15; \
	fi
	@touch $@

test: | setup
	# run testsuite
	DJANGO_SETTINGS_MODULE=dashboard.settings ${run} coverage run --include 'dashboard/*' \
		-m pytest -rap -k 'not integration and not system' ${testargs}
	# generate coverage
	${run} coverage report
	# and pretty html
	${run} coverage html
	# ensure no model updates are commited without migrations
	${run} dashboard makemigrations --check --dry-run

check: | setup
	@if test pyproject.yaml -nt poetry.lock; then \
		echo poetry.lock file not up to date, please run 'poetry lock'; \
		exit 1; \
	fi
	${run} pylama dashboard tests --skip "**/migrations/*"
	${run} isort --diff --check --recursive *

autofix fix: | setup
	# fix trivial pep8 style issues
	${run} autopep8 -ri dashboard tests
	# remove unused imports
	${run} autoflake -ri --remove-all-unused-imports dashboard tests
	# sort imports
	${run} isort -rc dashboard tests
	# do a check after autofixing to show remaining problems
	${run} pylama dashboard tests --skip "**/migrations/*"

test_integration: | setup
  	DB_NAME=test.sqlite3 ${run} pytest -v -k 'integration' ${testargs}

test_system:
	${run} pytest -v tests/system ${testargs}

test_image:
	docker-compose up

clean:
	rm -f db.sqlite
	rm -fr *.egg-info htmlcov
	rm -frI ${VIRTUAL_ENV}/
