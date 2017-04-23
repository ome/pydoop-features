set -eux

yum install -y cmake
pip install pytest
git clone --depth=1 -b master https://github.com/Byhiras/pyavroc.git
pushd pyavroc
git clone --depth=1 -b patches https://github.com/Byhiras/avro.git local_avro
./clone_avro_and_build.sh --static
python setup.py install --skip-build
popd
