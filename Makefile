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
env = env PATH=${bin}:$$PATH

# shortcuts for common used binaries
python = ${bin}/python
pip = ${bin}/pip
poetry = ${bin}/poetry

# application binary
app = ${bin}/${app_name}

$(info )
$(info Run `make help` for available commands or use tab-completion.)
$(info )

pysrcdirs = ${app_name}/
pysrc = $(shell find ${pysrcdirs} -name *.py)
shsrc = $(shell find * ! -path vendor\* -name *.sh)

.PHONY: test check setup run fix autofix clean mrproper poetry test_integration

# default action to run
all: check test setup

## Setup
# setup entire dev environment
setup: ${app}	## setup development environment and application
	@echo -ne "Development environment is tested and ready."
	@if command -v dashboard &>/dev/null;then \
		echo -e " Development shell is activated."; \
	else \
		echo -e "\n\nTo activate development shell run:"; \
		echo -e "\n\t. ${VIRTUAL_ENV}/bin/activate$$([[ "$$SHELL" =~ "fish" ]] && echo .fish)\n"; \
		echo -e "Or refer to Direnv in README.md for automatic activation."; \
	fi

# install application and all its (python) dependencies
${app}: poetry.lock | poetry
	# install project and its dependencies
	VIRTUAL_ENV=${VIRTUAL_ENV} ${poetry} install --develop=${app_name} ${poetry_args}
	@test -f $@ && touch $@

poetry.lock: pyproject.toml | poetry
	# update package version lock
	${env} poetry lock

poetry_update: pyproject.toml | poetry
	# Updating dependencies and locking them (test before committing)
	${env} poetry update

## QA
test: .make.test	## run test suite
.make.test: ${pysrc} ${app}
	# run testsuite
	DJANGO_SETTINGS_MODULE=${app_name}.settings ${env} coverage run --include '${app_name}/*' \
		-m pytest -k 'not integration and not system' ${testargs}
	# generate coverage
	${env} coverage report
	# and pretty html
	${env} coverage html
	# ensure no model updates are commited without migrations
	${env} ${app} makemigrations --check
	@touch $@

check: .make.check.py .make.check.sh  ## code quality checks
.make.check.py: ${pysrc} ${app}
	# check code quality
	${env} pylama ${pysrcdirs} --skip "**/migrations/*"
	@touch $@

.make.check.sh: ${shsrc}
	# shell script checks (if installed)
	if command -v shellcheck &>/dev/null && ! test -z "${shsrc}";then ${env} shellcheck ${shsrc}; fi
	@touch $@

autofix fix: .make.fix  ## automatic fix of trivial code quality issues
.make.fix: ${pysrc} ${app}
	# fix trivial pep8 style issues
	${env} autopep8 -ri ${pysrcdirs}
	# remove unused imports
	${env} autoflake -ri --remove-all-unused-imports ${pysrcdirs}
	# sort imports
	${env} isort -rc ${pysrcdirs}
	# do a check after autofixing to show remaining problems
	${MAKE} check
	@touch $@

## Running
run: ${app}  ## run complete application stack (frontend, worker, broker)
	# start server (this can take a while)
	DEBUG=1 NETWORK_SUPPORTS_IPV6=1 ${env} ${app} devserver

run-frontend: ${app}  ## only run frontend component
	DEBUG=1 NETWORK_SUPPORTS_IPV6=1 ${env} ${app} runserver

app: ${app}  ## perform arbitrary app commands
    ## For example: make app cmd=migrate
    # make app cmd="loaddata development"
    # make app cmd="help"
    # make app cmd="report -y municipality"
    # make app cmd="makemigrations"
    # make app cmd="migrate"
	DEBUG=1 NETWORK_SUPPORTS_IPV6=1 ${env} ${app} ${cmd}

run-worker: ${app}  ## only run worker component
	DEBUG=1 NETWORK_SUPPORTS_IPV6=1 ${env} ${app} celery worker -ldebug -Q storage,celery

run-broker:  ## only run broker
	docker run --rm --name=redis -p 6379:6379 redis

## Testing
test_integration: ${app}  ## perform integration test suite
	DB_NAME=test.sqlite3 ${env} pytest -v -k 'integration' ${testargs}

testcase: ${app}
	# run specific testcase
	# example: make test_testcase testargs=test_openstreetmaps
	${env} DJANGO_SETTINGS_MODULE=${app_name}.settings DB_NAME=test.sqlite3 \
		${env} pytest -k ${case}

test_datasets: ${app}
	${env} /bin/sh -ec "find ${app_name}/ -path '*/fixtures/*.yaml' -print0 | \
		xargs -0n1 basename -s .yaml | uniq | \
		xargs -n1 ${app} test_dataset"

test_deterministic: | ${VIRTUAL_ENV}
	${env} /bin/bash tools/compare_differences.sh HEAD HEAD tools/show_ratings.sh testdata

pull_image: image
	docker pull ${docker_image_name}

push_image: image
	docker push ${docker_image_name}

image build_image:  ## Create Docker image
	docker build -t ${docker_image_name} .

## Housekeeping
clean:  ## cleanup build artifacts, caches, databases, etc.
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

clean_virtualenv:  ## cleanup virtualenv and installed app/dependencies
	# clear poetry cache
	-yes yes | poetry cache:clear --all pypi
	# remove virtualenv
	-rm -fr ${VIRTUAL_ENV}/


#                                                          ....
#                                                   ,/%%%(//**/(%%%%(,.
#                                           .,*//(%%/.             .,(%%(///*,.
#                                      .*/*,...,%(.               ..,,,,%%*.,*//(/*.
#                                  .**,.......*%.        .........,,******%(     ,*/(/*,
#                              .**,......    *%.     ..,,,,,,,,****/**///**%/        .*/(/*.
#                           .**....          %*    .,,,,,,,,,,,,,**//(((((*(%.           */(//.
#                        .**...             .%.  .    .,,*,*******,.    ,(//%*              */(/*.
#                      ,*,..                ,%    .,,.    ,*,,*,    .... *(/%/                ./((/,
#                    .*..                   *(   /%(%%%%(,******,/%%%(//,.//%/                   *((/.
#                  ,*.                    ,(%%  *%%%/%%((%%%/*(%%/%%(/(/////%%(*                   ./(/,
#                ,*.                    .,%/**  ((*///((***/,*,,**((/**,,****,/%% .                  /((/,
#               *,                 ...,,,/(/*(  ,(*,...,,*/,,*,,,,,,,,,,..,///(%%...,......           ./((/.
#             ,*.              ...,,**////%*%/  .((*,,*//,*..,,,,*/*,.....*//%(%/,*,,,,,,,,,,......     *((/,
#            *,             ..,,,,***/////%%..   (%(%(/*%%%%%%%%/,,*(%/**//*/*%(****/*****,***,,,,,...   ,/((*
#          ./.            ..,,**,****///(((%%.   (%/(%%(////**,*,,,,/((%//***%(//////////**/*******,,.... ./(//.
#         .*.          ..,,******,,***//((((%*   /(//(%(((%(((((//**,**//**/%*(((//((/((///////////**,,,,.../((/.
#        ,/...      ...***////**,..**//((((((%*  ,(//%((%%/*,**/((*,,*,*///*/*%((((((((((((((((((((//*/***,,,/(((,
#       ,/,.........,,///((((////*////(((((((%(   ,%/(%%/*****,,,,,**,/((/(%%(((((((((((((((((((((((((/////***((((,
#      .(,,,......,,*/(/((((((((((((((((((((((%/    /%/(%/,,...,,,**/%%%((%%(((((%%%%%%%%%%%(((((((((((((((////((((.
#     .(*,,,,,,,,**//((((((%%%%%(((%%(%%%((((%%%,.*. ./(,%%(////(((%%%%%//%(%%%%%%%%%%%%%%%%%%%%%%%%(/((((((((((((((.
#     (/**,,,*****/((((%%%%%%%%(/,/(%%%%%(**((%%, *%%%%(%%(((%%%%%%%%%*,,/%(%%%%%%%%%%%%%%%%%%%%%%%%(//(%%%%%%%((%%%(
#    *(/*******//(((%%%%%%%%%%%%(((%%%%%%%((%%%%. .%%%%%%%%%%%%%%**//*,,,/%(%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%*
#   .((///**///(((%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  .%%%%%%%%%%%///((/,.,,,*%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%(.
#   *%////////((%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%,   (%%%%%%%%%/////*,..,,,,/%/%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%*
#   (%(((((((((%%%%%%%%%%%%%%%%%%%%%%%%%%%%/,.,*.  /%%%%%%%(******,,.,,,,/%%*  */%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%(
#  .%%(((((((%%%%%%%%%%%%%%%%%%%%%%%(/,.    ,.    .,////%%(/*,,,,,,,*/%%(,    ,*     .,/%%%%%%%%%%%%%%%%%%%%(((%%%%%%%%.
#  *%%%%((%%%%%%%%%%%%%%%%%%(/,.                       .*/(%%%%%%%%(*.     ..            ....,,*/(%%%%%%%%((//(((%%%%%%*
#  /%%%%%%%%%%%%%%%%%%*.                                                                      ....  ,%%%%%(/,.*((%%%%%%(
#  (%%%%%%%%%%%%%%%%..                                                                          ..... (%%%%(((((%%%%%%%(
#  (%%%%%%%%%%%%%%..,.                                                                            ..,. .%%%%%%%%%%%%%%%(
#  (%%%%%%%%%%%%% .,,     .,**//(/,..                                                              ..,...%%%%%%%%%%%%%%(
#  (%%%%%%%%%%%%  .,,./%*..,,,,,,,,*/%%.                                                  ..        .,,,..%%%&&&&&%%%%%(
#  *%%%%%%%%%%%  ..(%,..,...,,,,,,,,,,*%(.                                             *,,,.          .,,..%%%&&&&%%%%%*
#  .%%%%%%%%%%    .(%*.. ........,,*,,,,*(%/                 .,*/(%%%%%(/,..         .(,**,           .,*,.,%%%&&%%%%%%.
#   %%%%%%%%%.   .,,(%%%%%%%(%%(/*,,,*,,,,,%%.    .,*/(%%%%(*,,,,***,,,,,***//(%%/.  (*(%%%%%((((%%%%,.,**,.,%%%&%%%%%%
#   /%%%%%%%*   ./%%(,  /(((/*,,,*/((%%%%%((///*,,..     .,,******,,,,,,,**,,,,,,,*/%%%%((/***,,.,,,,(%%(**,.(%%%%%%%%/
#   .%%%%%%%  *%%*/,     ./%%%/*.                ..,,*****,,***,********,,****,,,**,,,,,/(//**,...,,,,,*%%%*.,%%%%%%%%.
#    /%%%%%/*%(  .*.   .,....,,,,***,.   .,,,***,,,,,,,,,,,,*****,,,**/(%%%(//*****/((/***(/*,,...,,,,,,,*/%%,(%%%%%%/
#     %%%%%%%,       .,***,,,,,,**,,***,,,,,,,,,,,********,,,,,**/%%%((%%%%%%%%%%%%%%%%((///****,**,,,,,,***/%%%%%%%%
#     .%%%%%*    ,/(/*,,,,,,,,,,,,***,,,,,*********,,,,,,,**/%%%((%%%%%%%%%%%%%%/*,,,,.......,,,,,,,,,,,,,****%%(%%%.
#      ,%%%%/ ./%%%(/************,,**********,,,,,,,,,*/(%%%%(%%/*,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,..,,,,,**/%%%%%,
#       *%%%(,(%%%%(/*******************,,,,,,,,,**/(%%%%%%%%/,******,,,,,,,,,,,,,,,,,,,,,,,,,,****,,,,,,*,,/%%%%%*
#        *%%((%%%%%%(//***********,,,,,,,,,,**/((%%%%%%%%%(***************************,,,,,,,,,,,**********,(%%%%*
#         *%(%%%%%%%%%(//****,,,,,,,,,***/(%%%%%%%%%%%%%%(((((////******,,,,,*****************,,,,,,,,,,,,**%%%%*
#         .%%%%%%%%%(/////*******////((%%%%%%%%%%%%%%%%%((%%%%%%%%%%%%%((//**,,,,,,,,,,****************,,,*/%%(,
#          (%((%%%%%%%(((/////((((%%%%%%%%%(%%%(******/(%%%%%%(((%%%%%%%%%%%%%%((//***,,,,,,,,,,,,,,,,,,,,,(%(
#           %%(%%%%%%%%%%%%%%%%%%%%%%%%(%%%(/****************/(%%%%%(((%%%%%%%%%%%%%%%%((((((//////**,,,,,,%%,
#           .%%%%%%%%%%%%%%%%%%((((%%%%(*,**************************/(%%%%((%%%%%%%%%%%%%%%%%%%%%%%%%%%%%((%%.
#             *%%%%((((((((%%%%%%/,,,,**,,********************************(%%%%(((%%%%%%%%%%%%%%%%%%%(((%%%%,
#                  ,%%%%%%%%%%%%%. .,*******************************************/%%%%%%%%%%%%%%%%((%%%%%/.
#                    ,%%%%%%%%%%%/ .,************************************************,,  %%%%%%%%%%%%,
#                      *%%%%%%%%%%. .************************************************,, *%%%%%%%%%%*
#                        .(%%%%%%%( .,************************************************/%%%%%%%%%(.
#                           ,%%%%%%%/*********************************************(%%%%%%%%%%%,
#                              ,(%%%%%%%%(***********************************/(%%%%%%%%%%%(,
#                                  *%%%%%%%%%%%((//***********,,,,**//(%%%%%%%%%%%%%%%%*
#                                      ,(%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%(,
#                                           ,/(%%%%%%%%%%%%%%%%%%%%%%%%%%%%%(/,
#                                                   ..,*//(((((((//*,..
mrproper: clean clean_virtualenv ## thorough cleanup, also removes virtualenv

## Base requirements

# don't let poetry manage the virtualenv, we do it ourselves to make it deterministic
poetry: ${poetry}
poetry_version=0.12.15
${poetry}: ${python}
	# install poetry
	${pip} install -q poetry==${poetry_version}

python: ${python}
${python}:
	@if ! command -v python3 &>/dev/null;then \
		echo "Python 3 is not available. Please refer to installation instructions in README.md"; \
	fi
	# create virtualenv
	python3 -mvenv ${VIRTUAL_ENV}
	# ensure a recent version of pip is used to avoid errors with intalling
	${VIRTUAL_ENV}/bin/pip install --upgrade pip==19.1.1


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
