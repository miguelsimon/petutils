#!/bin/bash

set -e

echo "Running integration tests for ${NEXUS:?}"

mkdir -p /integration-tests

echo "build nexus"
(cd ${NEXUS:?} && scons)
echo
echo "Running checks, outputs dumped in /integration-tests"
echo
for CHECK in check_*
do
  OUTPUT=/integration-tests/$CHECK.out
  printf "running $CHECK ... "
  if bash $CHECK &> $OUTPUT ; then
    printf "ok\n"
  else
    printf "FAILED\n"
  fi
done
