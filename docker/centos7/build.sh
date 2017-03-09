#!/bin/bash

set -eux

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
