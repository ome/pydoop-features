#!/usr/bin/env python

"""\
Convert avro file into an OMERO.features OMERO.tables HDF5 file.

Arguments:
- mapping.tsv: Mapping of OMERO IDs to avro records, produced by map_series.py
- output.h5: Output OMERO.features file, data will be appended if it exists
- inputs: One or more avro files to be converted
"""

import argparse
from collections import OrderedDict
import csv
import omero
import omero.tables
import os
import sys


from avro.datafile import DataFileReader
from avro.io import DatumReader


def parse_args(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'mapping', help='Mapping of OMERO IDs to avro records (tsv)')
    parser.add_argument(
        'output', help='Output OMERO.features file (append if exists)')
    parser.add_argument('inputs', nargs='+', help='Input avro files')
    return parser.parse_args(args)


def column_type(ctype, colname):
    ctypes = ctype.split()
    assert len(ctypes) in (1, 2)

    columntype = getattr(omero.columns, '%sColumnI' % ctypes[0])

    col = columntype(name=str(colname))
    if len(ctypes) == 2:
        col.size = int(ctypes[1])
    col.values = []
    return col


def get_image_ids(tsv):
    iids = {}
    with open(tsv) as f:
        r = csv.reader(f, delimiter='\t')
        header = r.next()
        assert header == ['PLATE', 'SERIES', 'WELL', 'FIELD', 'IMG_ID']
        for line in r:
            k = '%s_%s' % (line[0], line[1])
            iid = long(line[-1])
            assert k not in iids
            iids[k] = iid
    return iids


id_fields = OrderedDict([
    ('ImageID', 'Image')
])

metadata_fields = OrderedDict([
    # 'name',
    # 'series',
    # 'img_path',
    ('version', 'String 3'),
    ('x', 'Long'),
    ('y', 'Long'),
    ('c', 'Long'),
    ('z', 'Long'),
    ('t', 'Long'),
    ('w', 'Long'),
    ('h', 'Long'),
])

exclude_fields = (
    'name',
    'series',
    'img_path',
)


def convert_avro(f, iids, expected_features):
    """
    f: File handle to the input file
    iids: Map of plate-series to omero-image-ids
    expected_features: The list of expected features, if empty this will be
    populated by the first avro record
    """
    cols = []
    with DataFileReader(f, DatumReader()) as a:

        for i, r in enumerate(a):
            iid = iids[r['name']]
            print i, r['name'], iid

            all_fields = r.keys()
            feature_fields = sorted(set(all_fields).difference(
                metadata_fields.keys()).difference(exclude_fields))
            if expected_features:
                assert (
                    expected_features == feature_fields), 'Mismatched features'
            else:
                expected_features = feature_fields
            assert len(all_fields) == (
                len(feature_fields) + len(metadata_fields) + len(
                    exclude_fields)), 'Unexpected fields'

            if not cols:
                for mk, mv in id_fields.iteritems():
                    c = column_type(mv, mk)
                    assert mv == 'Image', 'Not implemented for non-image IDs'
                    cols.append(c)

                for mk, mv in metadata_fields.iteritems():
                    c = column_type(mv, mk)
                    cols.append(c)

                for fk in feature_fields:
                    size = len(r[fk])
                    if size > 0:
                        c = column_type('DoubleArray %d' % size, fk)
                        cols.append(c)

            for c in cols:
                if c.name == 'ImageID':
                    c.values.append(iid)
                else:
                    c.values.append(r[c.name])

    return cols


def main(argv):
    args = parse_args(argv[1:])
    iids = get_image_ids(args.mapping)
    fileout = os.path.abspath(args.output)
    expected_features = []

    for avroin in args.inputs:
        with open(avroin) as f:
            init_needed = not os.path.exists(fileout)
            cols = convert_avro(f, iids, expected_features)
            t = omero.tables.HDFLIST.getOrCreate(fileout)
            if init_needed:
                t.initialize(cols)
            t.append(cols)
            t.cleanup()

# If you want to read back the data use
# t._HdfStorage__mea.read_coordinates(range(t._HdfStorage__mea.nrows))


if __name__ == "__main__":
    main(sys.argv)
