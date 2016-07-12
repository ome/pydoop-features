set -ex

. /etc/profile

set -u

curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
python get-pip.py
pip install avro libtiff matplotlib

# clone dependencies with depth=1 to speed things up
git clone --depth=1 --branch='metadata52/merge/trigger' \
    https://github.com/snoopycrimecop/bioformats.git
git clone --depth=1 --branch='master' \
    https://github.com/wnd-charm/wnd-charm.git

git clone --branch='master' https://github.com/simleo/pydoop-features.git

# the Maven build needs to find a tag, but we've cut the history to depth 1
tag="v$(python set_bf_ver.py -n)"
pushd bioformats
git tag -a "${tag}" -m "tagging ${tag}"
mvn install -DskipTests
popd

python set_bf_ver.py

pushd wnd-charm
./build.sh
make install
python setup.py install
popd

pushd pydoop-features
python setup.py install
popd

cat <<EOF >/usr/local/bin/pyfeatures
#!/bin/bash
. /etc/profile
/opt/rh/python27/root/usr/bin/pyfeatures "\$@"
EOF
chmod +x /usr/local/bin/pyfeatures
