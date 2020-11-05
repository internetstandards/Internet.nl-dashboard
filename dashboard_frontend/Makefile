docker_image_name = internetstandards/dashboard-static

all: lint test

setup:

lint:
	# TODO

test:
	# TODO

vue-cli=node_modules/.bin/vue-cli-service
$(vue-cli):
	npm install
vue-cli: | $(vue-cli)

run-gui-development: vue-cli ## only run the gui
	# the extra -- is because of hell and fail. https://github.com/vuejs/vue-cli/issues/1528
	cd dashboard_frontend; npm run serve -- --mode development

build-gui-staging: vue-cli
	npm run build -- --mode staging

build-gui-production: vue-cli
	npm run build -- --mode production

pull_image:
	# optimize build by caching previously build image
	-docker pull ${docker_image_name}

push_image:
	docker push ${docker_image_name}

image:
	docker build -t ${docker_image_name} .

