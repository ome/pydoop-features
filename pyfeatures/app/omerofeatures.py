#!/usr/bin/env python

from collections import OrderedDict
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


filein = sys.argv[1]
fileout = os.path.abspath(sys.argv[2])


def column_type(ctype, colname):
    ctypes = ctype.split()
    assert len(ctypes) in (1, 2)

    columntype = getattr(omero.columns, '%sColumnI' % ctypes[0])

    col = columntype(name=str(colname))
    if len(ctypes) == 2:
        col.size = int(ctypes[1])
    return col


id_fields = OrderedDict([
    ('ImageID', 'Image')
    ])

metadata_fields = OrderedDict([
    ('series', 'Long'),
    # 'name',
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
    'img_path',
    # 'version',
)


f = open(filein)
a = AvroFileReader(f)
cols = []
for i, r in enumerate(a):
    print i
    if not cols:
        all_fields = r.keys()
        feature_fields = sorted(set(all_fields).difference(
            metadata_fields.keys()).difference(exclude_fields))
        assert len(
            all_fields) == len(feature_fields) + len(metadata_fields) + len(
                exclude_fields)

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
            c.values.append(r[c.name])

init_needed = not os.path.exists(fileout)
t = omero.tables.HDFLIST.getOrCreate(fileout)
if init_needed:
    t.initialize(cols)
t.append(cols)

#t._HdfStorage__mea.read_coordinates(range(t._HdfStorage__mea.nrows))

t.cleanup()
a.close()
f.close()
