workflow "Release" {
  on = "push"

  resolves = [
    "Check",
    "Test",
  ]
}

action "Check" {
  uses = "docker://python:3.6"
  runs = ["/bin/sh", "-c", "pip install tox; tox -e check"]
}

action "Test" {
  needs = "Check"
  uses = "docker://python:3.6"
  runs = ["/bin/sh", "-c", "pip install tox; tox -e test"]
}
