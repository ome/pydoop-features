set -ex

. /etc/profile

set -u

easy_install pip

git clone https://github.com/openmicroscopy/bioformats.git
git clone https://github.com/wnd-charm/wnd-charm.git
git clone https://github.com/simleo/pydoop-features.git

pushd bioformats
git checkout metadata
mvn install -DskipTests
popd

python set_bf_ver.py
pip install avro
pip install libtiff

pushd pydoop-features
mvn clean compile assembly:single
popd

pushd wnd-charm
./build.sh
make install
python setup.py install
popd
