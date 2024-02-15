#!/bin/bash
# check to pull latest version, if needed
docker pull registry.gitlab.com/ska-telescope/src/src-workloads/cross-matching:latest
# run container pipeline
docker run -it --rm --name cross-matching -t -v "$(pwd)"/scripts:/scripts/ registry.gitlab.com/ska
-telescope/src/src-workloads/cross-matching:latest
