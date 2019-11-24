#!/bin/bash

set -e

cd ${NEXUS:?}

# remove output file if it exists
rm -f petit_ring.pet.h5

./nexus -b -n 100 macros/PETit_ring.init.mac

# assert it generated h5 file
test -f petit_ring.pet.h5

# check file format with petutils
python3 -m petutils.utils check_file --hdf5_file petit_ring.pet.h5
