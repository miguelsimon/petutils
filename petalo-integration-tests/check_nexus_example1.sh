#!/bin/bash

set -e

cd ${NEXUS:?}
./nexus -b -n 100 macros/nexus_example1.init.mac
