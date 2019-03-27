workflow "Release" {
  on = "push"

  resolves = [
    "check",
    "test",
    "build",
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

action "build" {
  needs = ["check", "test"]
  uses = "actions/docker/cli@master"
  args = "build -t dashboard ."
}