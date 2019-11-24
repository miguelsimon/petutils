#!/bin/bash

set -e

cd ${NEXUS:?}

./nexus -b -n 100 macros/PETit_ring.init.mac
