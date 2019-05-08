all: check test

VIRTUAL_ENV := $(shell poetry config settings.virtualenvs.path|tr -d \")/dashboard-py3.6
export PATH := ${VIRTUAL_ENV}/bin:${PATH}

setup: ${VIRTUAL_ENV}/bin/dashboard

${VIRTUAL_ENV}/bin/dashboard: poetry.lock
	poetry install --develop=dashboard
	test -f $@ && touch $@

poetry.lock: pyproject.toml
	poetry lock

test: | setup
	# run testsuite
	DJANGO_SETTINGS_MODULE=dashboard.settings coverage run --include 'dashboard/*' \
		-m pytest -rap -k 'not integration and not system' ${testargs}
	# generate coverage
	coverage report
	# and pretty html
	coverage html
	# ensure no model updates are commited without migrations
	dashboard makemigrations --check

check: | setup
	pylama dashboard tests --skip "**/migrations/*"
	isort --diff --check --recursive *

autofix fix: | setup
	# fix trivial pep8 style issues
	autopep8 -ri dashboard tests
	# remove unused imports
	autoflake -ri --remove-all-unused-imports dashboard tests
	# sort imports
	isort -rc dashboard tests
	# do a check after autofixing to show remaining problems
	pylama dashboard tests --skip "**/migrations/*"

test_integration: | setup
  	DB_NAME=test.sqlite3 pytest -v -k 'integration' ${testargs}

test_system:
	pytest -v tests/system ${testargs}

test_datasets: | setup
	/bin/sh -ec "find dashboard -path '*/fixtures/*.yaml' -print0 | \
		xargs -0n1 basename -s .yaml | uniq | \
		xargs -n1 dashboard test_dataset"

test_deterministic: | ${virtualenv}
	/bin/bash tools/compare_differences.sh HEAD HEAD tools/show_ratings.sh testdata

test_mysql:
	docker run --name mysql -d --rm -p 3306:3306 \
		-e MYSQL_ROOT_PASSWORD=failmap \
		-e MYSQL_DATABASE=failmap \
		-e MYSQL_USER=failmap \
		-e MYSQL_PASSWORD=failmap \
		-v $$PWD/tests/etc/mysql-minimal-memory.cnf:/etc/mysql/conf.d/mysql.cnf \
		mysql:5.6
	DJANGO_DATABASE=production DB_USER=root DB_HOST=127.0.0.1 \
		$(MAKE) test; e=$$?; docker stop mysql; exit $$e

test_postgres:
	docker run --name postgres -d --rm -p 5432:5432 \
		-e POSTGRES_DB=failmap \
		-e POSTGRES_USER=root \
		-e POSTGRES_PASSWORD=failmap \
		postgres:9.4
	DJANGO_DATABASE=production DB_ENGINE=postgresql_psycopg2 DB_USER=root DB_HOST=127.0.0.1 \
		$(MAKE) test; e=$$?; docker stop postgres; exit $$e

clean:
	rm -fr ${VIRTUAL_ENV}/{bin,include,lib,share,*.cfg,*.json}
	test -d ${VIRTUAL_ENV} && rmdir ${VIRTUAL_ENV} || true
