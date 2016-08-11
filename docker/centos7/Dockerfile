FROM centos:7
MAINTAINER ome-devel@lists.openmicroscopy.org.uk

COPY build.sh install_maven.sh set_bf_ver.py install_pydoop_features.sh /
RUN bash /build.sh

RUN useradd -m features

USER features
ENV HOME /home/features

ENTRYPOINT ["/usr/bin/pyfeatures"]
