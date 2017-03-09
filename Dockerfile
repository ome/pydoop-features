FROM centos:7
MAINTAINER ome-devel@lists.openmicroscopy.org.uk

COPY docker/centos7 /build

COPY pom.xml /build/
COPY setup.py /build
COPY setup.cfg /build

COPY src /build/src
COPY pyfeatures /build/pyfeatures

WORKDIR /build/
RUN bash build.sh

# TODO: re-order later
COPY scripts /build/scripts
RUN bash -ic "python setup.py install"
RUN yum -y install tkinter

RUN useradd -m features

USER features
ENV HOME /home/features

ENTRYPOINT ["/usr/bin/pyfeatures"]
