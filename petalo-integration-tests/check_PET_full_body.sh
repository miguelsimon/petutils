#!/bin/bash

set -e

cd ${NEXUS:?}

echo "clean up files (otherwise it'll segfault)"
rm -rf GenerationAngles.root \
  PET_full_body.init.history \
  PET_full_body.config.history \
  full_body.pet.h5

./nexus -b -n 100 macros/PET_full_body.init.mac
