#!/usr/bin/env bash

# generate a new version number based on most recent tag and commit sha

tag_version=$(git describe --tags --abbrev=0)

sha=$(git rev-parse HEAD)
short_sha=${sha:0:8}

echo "${tag_version}+$short_sha"
