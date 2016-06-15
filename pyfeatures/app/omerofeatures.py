#!/usr/bin/env python

from collections import OrderedDict
import csv
import omero
import omero.tables
import os
import sys


from avro.datafile import DataFileReader
from avro.io import DatumReader


class AvroFileReader(DataFileReader):

    def __init__(self, f, types=False):
        if types:
            raise RuntimeError('types not supported')
        super(AvroFileReader, self).__init__(f, DatumReader())


args = sys.argv
assert len(args) == 4, 'Required arguments: in.avro mapping.tsv out.h5'
avroin = args[1]
tsvin = args[2]
fileout = os.path.abspath(args[3])


def column_type(ctype, colname):
    ctypes = ctype.split()
    assert len(ctypes) in (1, 2)

    columntype = getattr(omero.columns, '%sColumnI' % ctypes[0])

    col = columntype(name=str(colname))
    if len(ctypes) == 2:
        col.size = int(ctypes[1])
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
    # 'version',
)


f = open(avroin)
a = AvroFileReader(f)
iids = get_image_ids(tsvin)
cols = []

for i, r in enumerate(a):
    iid = iids[r['name']]
    print i, r['name'], iid

    if not cols:
        all_fields = r.keys()
        feature_fields = sorted(set(all_fields).difference(
            metadata_fields.keys()).difference(exclude_fields))
        assert len(
            all_fields) == len(feature_fields) + len(metadata_fields) + len(
                exclude_fields), 'Unexpected fields'

        for mk, mv in id_fields.iteritems():
            c = column_type(mv, mk)
            assert mv == 'Image', 'Not implemented for non-image IDs'
            c.values = [iid]
            cols.append(c)

        for mk, mv in metadata_fields.iteritems():
            c = column_type(mv, mk)
            c.values = [r[mk]]
            cols.append(c)

        for fk in feature_fields:
            size = len(r[fk])
            if size > 0:
                c = column_type('DoubleArray %d' % size, fk)
                c.values = [r[fk]]
                cols.append(c)

    else:
        for c in cols:
            if c.name == 'ImageID':
                c.values.append(iid)
            else:
                c.values.append(r[c.name])


init_needed = not os.path.exists(fileout)
t = omero.tables.HDFLIST.getOrCreate(fileout)
if init_needed:
    t.initialize(cols)
t.append(cols)

# t._HdfStorage__mea.read_coordinates(range(t._HdfStorage__mea.nrows))

t.cleanup()
a.close()
f.close()
