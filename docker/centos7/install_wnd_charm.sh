set -ex

. /etc/profile

set -u

git config --get user.email || git config --global user.email ome-devel@lists.openmicroscopy.org.uk
git config --get user.name || git config --global user.name omedev

curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
python get-pip.py
pip install avro libtiff matplotlib

git clone --depth=1 --branch='master' \
    https://github.com/wnd-charm/wnd-charm.git

pushd wnd-charm
./build.sh
make install
python setup.py install
popd
