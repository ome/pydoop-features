#!/usr/bin/env python

"""\
Convert avro file into an OMERO.features OMERO.tables HDF5 file.

Arguments:
- mapping.tsv: Mapping of OMERO IDs to avro records, produced by map_series.py
    Any columns matching regexp '^\w+ID$' will be included in the output
- output.h5: Output OMERO.features file, data will be appended if it exists
- inputs: One or more avro files to be converted
"""

import argparse
from collections import OrderedDict
import csv
import omero
import omero.tables
import os
import re
import sys
from time import time


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


def parse_header(header):
    # E.g. ['PLATE', 'SERIES', 'WELL', 'FIELD', 'Image_ID', 'Well_ID']
    headermap = OrderedDict((v, k) for (k, v) in enumerate(header))
    assert 'PLATE' in headermap
    assert 'SERIES' in headermap
    idmap = OrderedDict((h, p) for (h, p) in headermap.iteritems()
                        if re.match('\w+ID$', h))
    return headermap, idmap


def get_omero_ids(tsv):
    with open(tsv) as f:
        r = csv.reader(f, delimiter='\t')
        headermap, idmap = parse_header(r.next())

        # Mapping of OMERO.features ID columns:types e.g. ('ImageID', 'Image')
        id_fields = OrderedDict((h, h[:-2]) for h in idmap)
        omero_ids = dict((h, {}) for h in idmap)

        for line in r:
            k = '%s_%s' % (line[headermap['PLATE']], line[headermap['SERIES']])
            for idh, idp in idmap.iteritems():
                oid = long(line[idp])
                assert k not in omero_ids[idh]
                omero_ids[idh][k] = oid
    return omero_ids, id_fields


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


def convert_avro(f, omero_ids, id_fields, expected_features):
    """
    f: File handle to the input file
    iids: Map of plate-series to omero-image-ids
    expected_features: The list of expected features, if empty this will be
    populated by the first avro record
    """
    cols = []
    with DataFileReader(f, DatumReader()) as a:

        for i, r in enumerate(a):
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
                if c.name.endswith('ID'):
                    oid = omero_ids[c.name][r['name']]
                    c.values.append(oid)
                else:
                    c.values.append(r[c.name])

    return cols


def main(argv):
    args = parse_args(argv[1:])
    omero_ids, id_fields = get_omero_ids(args.mapping)
    fileout = os.path.abspath(args.output)
    expected_features = []

    start = time()
    for avroin in args.inputs:
        with open(avroin) as f:
            print 'Converting %s' % avroin
            init_needed = not os.path.exists(fileout)
            cols = convert_avro(f, omero_ids, id_fields, expected_features)
            t = omero.tables.HDFLIST.getOrCreate(fileout)
            if init_needed:
                t.initialize(cols)
            t.append(cols)
            t.cleanup()
            print '\tCumulative time: %d seconds' % (time() - start)

    print 'Done'

# If you want to read back the data use
# t._HdfStorage__mea.read_coordinates(range(t._HdfStorage__mea.nrows))


if __name__ == "__main__":
    main(sys.argv)
