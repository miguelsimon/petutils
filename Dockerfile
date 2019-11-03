FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
  build-essential \
  cmake \
  expat \
  libexpat-dev \
  scons \
  freeglut3 freeglut3-dev mesa-utils qt5-default libxmu-dev libxi-dev

COPY deps/geant4.10.05.p01 /geant4
COPY deps/root /cern-root
COPY deps/GATE /GATE
COPY deps/gsl-2.6 /gsl
COPY deps/hdf5-1.10.5 /hdf5

WORKDIR /

RUN mkdir /geant4-build

WORKDIR /geant4-build

RUN cmake -DCMAKE_INSTALL_PREFIX=/geant4-install /geant4
RUN cmake \
  -DGEANT4_INSTALL_DATA=ON \
  -DGEANT4_USE_OPENGL_X11=ON \
  -DGEANT4_USE_QT=ON \
  -DGEANT4_BUILD_MULTITHREADED=ON \
  .
RUN make -j2
RUN make install

ENV G4INSTALL=/geant4-install
ENV PATH="/geant4-install/bin:${PATH}"
ENV LD_LIBRARY_PATH="/geant4-install/lib:${LD_LIBRARY_PATH}"

ENV G4LEVELGAMMADATA=/geant4-install/share/Geant4-10.5.1/data/PhotonEvaporation5.3
ENV G4LEDATA=/geant4-install/share/Geant4-10.5.1/data/G4EMLOW7.7
ENV G4RADIOACTIVEDATA=/geant4-install/share/Geant4-10.5.1/data/RadioactiveDecay5.3
ENV G4ENSDFSTATEDATA=/geant4-install/share/Geant4-10.5.1/data/G4ENSDFSTATE2.2
ENV G4SAIDXSDATA=/geant4-install/share/Geant4-10.5.1/data/G4SAIDDATA2.0
ENV G4PARTICLEXSDATA=/geant4-install/share/Geant4-10.5.1/data/G4PARTICLEXS1.1
ENV G4NEUTRONHPDATA=/geant4-install/share/Geant4-10.5.1/data/G4NDL4.5

# install root

ENV ROOTSYS=/cern-root
ENV PATH="/cern-root/bin:${PATH}"
ENV LD_LIBRARY_PATH="/cern-root/lib:${LD_LIBRARY_PATH}"

# install GATE git@next.ific.uv.es:nextsw/GATE.git

WORKDIR /GATE
RUN make

ENV GATE_DIR=/GATE
ENV LD_LIBRARY_PATH="/GATE/lib:${LD_LIBRARY_PATH}"

# pcm files need to be next to .so files see https://github.com/lcfiplus/LCFIPlus/issues/17
RUN cp /GATE/emodel/GATECint_rdict.pcm /GATE/lib/
RUN cp /GATE/IO/GATEIOCint_rdict.pcm /GATE/lib/


# install gsl

WORKDIR /gsl
RUN ./configure
RUN make
RUN make install

ENV LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH}"

# install hdf5

WORKDIR /hdf5

RUN ./configure
RUN make
RUN make install
RUN make check-install

ENV LD_LIBRARY_PATH="/hdf5/hdf5/lib:${LD_LIBRARY_PATH}"
ENV HDF5_LIB="/hdf5/hdf5/lib"
ENV HDF5_INC="/hdf5/hdf5/include"

# install nexus

COPY deps/nexus /nexus

WORKDIR /nexus
RUN scons

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
  xorg openbox x11vnc xvfb dbus-x11 fluxbox locales

RUN locale-gen en_US.UTF-8
RUN update-locale LC_ALL=en_US.UTF-8

ENV LANG en_US.UTF-8  
ENV LC_ALL en_US.UTF-8

RUN mkdir ~/.vnc/ && x11vnc -storepasswd 1234 ~/.vnc/passwd
ENV DISPLAY=:1
ENTRYPOINT Xvfb :1 -screen 0 1024x768x16 & \
  fluxbox & \
  x11vnc -display :1 -usepw -shared -forever -bg && /bin/bash
