set -ex

. /etc/profile

set -u

easy_install pip

# clone dependencies with depth=1 to speed things up
git clone --depth=1 --branch='metadata/merge/trigger' \
    https://github.com/snoopycrimecop/bioformats.git
git clone --depth=1 --branch='master' \
    https://github.com/wnd-charm/wnd-charm.git

git clone --branch='master' https://github.com/simleo/pydoop-features.git

pushd bioformats
# the Maven build needs to find a tag, but we've cut the history to depth 1
git tag -a v5.1.8-METADATA-MERGE -m "tagging v5.1.8-METADATA-MERGE"
mvn install -DskipTests
popd

python set_bf_ver.py
pip install avro
pip install libtiff

pushd wnd-charm
./build.sh
make install
python setup.py install
popd

pushd pydoop-features
mvn clean compile assembly:single
python setup.py install
popd
