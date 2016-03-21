FROM centos:centos6
MAINTAINER simone.leo@crs4.it

RUN yum -y update
RUN yum -y install centos-release-SCL epel-release
RUN yum -y install \
    fftw-devel \
    fftw-static \
    gcc-c++ \
    git \
    java-1.8.0-openjdk-devel \
    libtiff-devel \
    python27 \
    python27-devel \
    python27-scipy \
    swig \
    tar
RUN echo ". /opt/rh/python27/enable" >/etc/profile.d/python.sh
COPY install_maven.sh /
RUN bash install_maven.sh
COPY set_bf_ver.py /
COPY install_pydoop_features.sh /
RUN bash install_pydoop_features.sh
RUN useradd -m features

USER features
ENV HOME /home/features

ENTRYPOINT ["/usr/local/bin/pyfeatures"]
