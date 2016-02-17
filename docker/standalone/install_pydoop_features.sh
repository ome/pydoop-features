set -eux

. /etc/profile
. /opt/rh/python27/enable

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

pushd pydoop-features
mvn install -DskipTests
popd

pushd wnd-charm
./build.sh
make install
python setup.py install
popd
