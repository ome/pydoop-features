pydoop-features
===============

What
----

Pydoop-features is a suite of tools for extracting features from image
data. It uses
[Bio-Formats](http://www.openmicroscopy.org/site/products/bio-formats)
to read image data, [Avro](https://avro.apache.org) for
(de)serialization and
[WND-CHARM](https://github.com/wnd-charm/wnd-charm) for feature
calculation.

How
---

The fastest way to get a working installation is to pull the
[Docker](https://www.docker.com) image:

    docker pull simleo/pyfeatures

Java-Python interoperability is achieved via Avro. The input dataset
can be in [any format supported by
Bio-Formats](https://www.openmicroscopy.org/site/support/bio-formats5.1/supported-formats.html). For
instance, download
[MF-2CH-Z-T](http://www.loci.wisc.edu/files/software/data/MF-2CH-Z-T.zip)
and unpack it under `/tmp`. The first step is to serialize this data
to Avro:

    docker run -u ${UID} --rm -v /tmp:/tmp simleo/pyfeatures \
      serialize /tmp/MF-2CH-Z-T.tif -o /tmp/

You should get one avro container file per image series in the input
dataset. In this case:

    /tmp/MF-2CH-Z-T_{0,1,2,3,4}.avro

To compute features for the first avro container:

    docker run -u ${UID} --rm -v /tmp:/tmp simleo/pyfeatures \
      calc /tmp/MF-2CH-Z-T_0.avro -o /tmp/

You might want to get a cup of coffee, feature calculation takes time.

When the above finishes, you should have the following file:

    /tmp/MF-2CH-Z-T_0_features.avro

which can be read from either Java or Python. For instance:

    >>> from avro.datafile import DataFileReader
    >>> from avro.io import DatumReader, BinaryDecoder
    >>> with open("/tmp/MF-2CH-Z-T_0_features.avro") as f:
    ...     reader = DataFileReader(f, DatumReader())
    ...     records = [_ for _ in reader]
    ...
    >>> len(records)
    40
    >>> r = records[0]
    >>> r['haralick_textures']
    [0.0015474594757607179, 0.00029323128834782644, ...]
