pydoop-features
===============

How to run a standalone (no Hadoop) version of the code
-------------------------------------------------------

In `pom.xml`, change `bio-formats.version` to whatever version of
Bio-Formats you'd like to use (`DFSHandle` is not needed since we're
not going to read from HDFS).

Serialize image data with Avro:

    mvn package
    cd scripts
    ./serialize /path/to/image/file.ext

At this point, you should have *N* Avro container files
(`file_${i}.avro`) in the top repo dir, where *N* is the number of
series in the input file.

Install the Python bindings for
[Avro](https://avro.apache.org). Since the official Python libraries
are very slow, you might want to install
[pyavroc](https://github.com/Byhiras/pyavroc) instead.

Install [WND-CHARM](https://github.com/wnd-charm/wnd-charm). Use the
provided `build.sh` script if you have problems with autotools:

    ./build.sh
    make install
    python setup.py install

You can compute features for each avro container with:

    python local_features.py ../file_${i}.avro

Feature vectors will be serialized to `file_${i}_features.avro`
files, which can be read from either Java or Python. For instance:

    >>> from pyavroc_emu import AvroFileReader
    >>> with open("file_0_features.avro") as f:
    ...     reader = AvroFileReader(f)
    ...     records = [_ for _ in reader]
    ...
    >>> r = records[0]
    >>> r['feature_names'][0]
    u'Chebyshev-Fourier Coefficients () [0]'
    >>> r['values'][0]
    465.0
