workflow "Release" {
  on = "push"

  resolves = [
    "check",
    "test",
    "test image",
    "test integration",
    "push image"
  ]
}

action "check" {
  uses = "./.github/action/build"
  args = ["check"]
}

action "test" {
  uses = "./.github/action/build"
  args = ["test"]
}

action "build image" {
  needs = ["check", "test"]
  uses = "actions/docker/cli@master"
  args = "build -t internetstandards/dashboard ."
}

action "test image" {
  needs = ["build image"]
  uses = "actions/docker/cli@master"
  args = "run internetstandards/dashboard help"
}

action "compose" {
  needs = ["test image"]
  uses = "docker://python:3.6"
  runs = ["/bin/sh", "-c", "pip install docker-compose; docker-compose up"]
  env  = {PIP_DISABLE_PIP_VERSION_CHECK="1"}
}

action "test integration" {
  needs = ["compose"]
  uses = "actions/docker/sh@master"
  args = "curl -sS http://localhost:8000/|grep MSPAINT"
}

action "authenticate registry" {
  uses = "actions/docker/login@master"
  secrets = ["DOCKER_USERNAME", "DOCKER_PASSWORD"]
}

action "push image" {
  needs = ["test integration", "authenticate registry"]
  uses = "actions/docker/cli@master"
  args = "push internetstandards/dashboard"
}
