set -eux

install_pyavroc() {
    pip install pytest
    pushd /tmp
    git clone --depth=1 -b master https://github.com/Byhiras/pyavroc.git
    pushd pyavroc
    git clone --depth=1 -b patches https://github.com/Byhiras/avro.git \
	local_avro
    ./clone_avro_and_build.sh --static
    python setup.py install --skip-build
    popd
    popd
}

case "${1}" in
    "avro")
	pip install avro
	;;
    "pyavroc")
	install_pyavroc
	;;
    *)
	echo "Usage: bash $0 [avro|pyavroc]" 1>&2
	exit 1
esac
