#!/bin/bash

set -ex

if [ -n "$BIOFORMATS_GROUPID" ]; then
    sed -i -re \
    "s%(<bio-formats.groupid>).+(</bio-formats.groupid>)%\1$BIOFORMATS_GROUPID\2%" \
    pom.xml
fi
if [ -n "$BIOFORMATS_VERSION" ]; then
    sed -i -re \
    "s%(<bio-formats.version>).+(</bio-formats.version>)%\1$BIOFORMATS_VERSION\2%" \
    pom.xml
fi

yum -y install epel-release
yum -y install \
    fftw-devel \
    fftw-static \
    freetype-devel \
    gcc-c++ \
    git \
    java-1.8.0-openjdk-devel \
    libpng-devel \
    libtiff-devel \
    make \
    python-devel \
    scipy \
    swig

bash /build/install_maven.sh
bash /build/install_wnd_charm.sh
bash /build/install_pyavroc.sh

yum clean all
