FROM centos:7
MAINTAINER ome-devel@lists.openmicroscopy.org.uk

COPY docker/centos7 /build

RUN yum -y -q install epel-release && \
    yum -y -q install ansible
# git is needed until openmicroscopy.omego is put on galaxy
RUN yum -y -q install git
RUN ansible-galaxy install -r /build/requirements.yml && \
    ansible-playbook /build/deps.yml

WORKDIR /build/

COPY pyfeatures /build/pyfeatures
COPY scripts /build/scripts
COPY src /build/src
COPY pom.xml setup.py setup.cfg /build/

RUN bash build.sh

RUN bash -ic "python setup.py install"
RUN yum -y install tkinter

RUN useradd -m features
ARG OMEGO_OPTS
RUN /opt/omero/omego/bin/omego download py --sym OMERO.py $OMEGO_OPTS

RUN printf 'PATH=$PATH:/build/OMERO.py/bin\n' > /etc/profile.d/omero.sh && \
    printf '/build/OMERO.py/lib/python\n' > /usr/lib/python2.7/site-packages/omero.pth

USER features
ENV HOME /home/features

ENTRYPOINT ["/usr/bin/pyfeatures"]
