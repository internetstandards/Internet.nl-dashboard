#!/bin/bash

# wrap a command in a auto reload watchdog to restart it if files change, useful for debugging inside docker

exec .venv/bin/watchmedo auto-restart -d websecmap/ -p "*.py" -R --signal SIGKILL -- "$@"
