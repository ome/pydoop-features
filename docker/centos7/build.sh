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

bash install_maven.sh
bash install_pydoop_features.sh

yum clean all
