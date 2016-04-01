set -eux

pushd /tmp
# clone with depth=1 to speed things up
git clone --depth=1 --branch='master' \
    https://github.com/wnd-charm/wnd-charm.git
pushd wnd-charm
./build.sh
python setup.py install
popd
popd
