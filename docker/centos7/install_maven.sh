set -eux

VERSION="3.3.9"
TAR="apache-maven-${VERSION}-bin.tar.gz"
REPO="ftp://ftp.mirrorservice.org/sites/ftp.apache.org/maven/maven-3"
MVN_HOME="/usr/local/apache-maven"
JAVA_HOME=$(dirname "$(dirname "$(readlink -e "$(type -P java)")")")

curl -o ${TAR} ${REPO}/${VERSION}/binaries/${TAR}
tar xvf ${TAR}
mv apache-maven-${VERSION} ${MVN_HOME}

cat >/etc/profile.d/maven.sh <<EOF
export JAVA_HOME="${JAVA_HOME}"
export M2_HOME="${MVN_HOME}"
export M2="\${M2_HOME}/bin"
export PATH="\${M2}:\${PATH}"
EOF
