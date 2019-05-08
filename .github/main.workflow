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
  uses = "docker://python:3.6"
  runs = ["/bin/sh", "-c", "pip install poetry; make check"]
}

action "test" {
  uses = "docker://python:3.6"
  runs = ["/bin/sh", "-c", "pip install poetry; make test"]
}

action "build image" {
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
  needs = ["test integration", "check", "test", "authenticate registry"]
  uses = "actions/docker/cli@master"
  args = "push internetstandards/dashboard"
}
