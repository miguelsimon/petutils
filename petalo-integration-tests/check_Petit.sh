#!/bin/bash

set -e

cd ${NEXUS:?}
./nexus -b -n 100 macros/Petit.init.mac
