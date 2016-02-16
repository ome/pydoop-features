FROM centos:centos6
MAINTAINER simone.leo@crs4.it

ADD install_maven.sh /

RUN yum -y update
RUN yum -y install \
    tar \
    java-1.8.0-openjdk-devel
RUN bash install_maven.sh
RUN source /etc/profile
