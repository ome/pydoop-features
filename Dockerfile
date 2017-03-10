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
RUN pip install omego \
 && omego download server --release=0.3.3 --downloadurl=https://downloads.openmicroscopy.org/idr

RUN find /build -type d -name "OMERO.server*" -maxdepth 1 -exec ln -s {} /build/OMERO.server \;
RUN printf 'PATH=$PATH:/build/OMERO.server/bin\n' > /etc/profile.d/omero.sh \
 && printf 'PYTHONPATH=$PYTHONPATH:/build/OMERO.server/lib/python\n' >> /etc/profile.d/omero.sh

COPY docker/centos7/deps.yml /build/
RUN yum -y install epel-release \
 && yum -y install ansible
RUN ansible-galaxy install openmicroscopy.ice \
 && ansible-playbook /build/deps.yml

RUN printf '/build/OMERO.server/lib/python\n' > /usr/lib/python2.7/site-packages/omero.pth

USER features
ENV HOME /home/features

ENTRYPOINT ["/usr/bin/pyfeatures"]
