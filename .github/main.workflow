workflow "Release" {
  on = "push"

  resolves = [
    "check",
    "test",
    "test image",
    "test integration"
  ]
}

action "check" {
  uses = "docker://python:3.6"
  runs = ["/bin/sh", "-c", "pip install tox; tox -e check"]
  env = {
    TOX_WORK_DIR = "/tmp"
  }
}

action "test" {
  uses = "docker://python:3.6"
  runs = ["/bin/sh", "-c", "pip install tox; tox -e test"]
  env = {
    TOX_WORK_DIR = "/tmp"
  }
}

action "build image" {
  uses = "actions/docker/cli@master"
  args = "build -t dashboard ."
}

action "test image" {
  needs = ["build image"]
  uses = "actions/docker/cli@master"
  args = "run dashboard help"
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
