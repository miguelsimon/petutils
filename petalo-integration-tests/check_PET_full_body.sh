#!/bin/bash

set -e

cd ${NEXUS:?}

./nexus -b -n 100 macros/PET_full_body.init.mac
