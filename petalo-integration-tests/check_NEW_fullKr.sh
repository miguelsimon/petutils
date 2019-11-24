#!/bin/bash

set -e

cd ${NEXUS:?}
./nexus -b -n 100 macros/NEW_fullKr.init.mac
