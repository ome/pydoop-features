FROM centos:7
MAINTAINER ome-devel@lists.openmicroscopy.org.uk

RUN yum -y install epel-release
RUN yum -y install \
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

COPY install_maven.sh /
RUN bash install_maven.sh
COPY set_bf_ver.py /
COPY install_pydoop_features.sh /
RUN bash install_pydoop_features.sh
RUN useradd -m features

USER features
ENV HOME /home/features

ENTRYPOINT ["/usr/bin/pyfeatures"]
