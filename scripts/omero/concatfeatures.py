#!/usr/bin/env python

# BEGIN_COPYRIGHT
#
# Copyright (C) 2016-2017 Open Microscopy Environment:
#   - University of Dundee
#   - CRS4
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# END_COPYRIGHT

"""\
Concat multiple OMERO.tables into one.

Arguments:
- output.h5: Output table
- inputs: One or more tables to be converted
"""

import argparse
import os
from shutil import copyfile
import sys
import tables
from time import time

# Number of rows to read at a time
ROW_CHUNK = 1024


def parse_args(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'output', help='Output OMERO.table file (append if exists)')
    parser.add_argument('inputs', nargs='+', help='Input OMERO.tables files')
    return parser.parse_args(args)


def main(argv):
    args = parse_args(argv[1:])

    fileout = os.path.abspath(args.output)

    start = time()
    for fin in args.inputs:
        filein = os.path.abspath(fin)
        print 'Concatenating %s' % filein
        if not os.path.exists(fileout):
            copyfile(filein, fileout)
        else:
            # Can't use HdfStorage.readCoordinates because it needs an
            # Ice.Communicator object, so there's no point using the
            # OMERO.tables interface
            tout = tables.open_file(fileout, 'r+')
            tin = tables.open_file(filein, 'r')
            nrows = tin.root.OME.Measurements.nrows

            for a in range(0, nrows, ROW_CHUNK):
                b = min(nrows, a + ROW_CHUNK)
                print '\tRows %d:%d' % (a, b)
                rows = tin.root.OME.Measurements.read_coordinates(range(a, b))
                tout.root.OME.Measurements.append(rows)

            tin.close()
            tout.close()
        print '\tCumulative time: %d seconds' % (time() - start)

    print 'Done'


if __name__ == "__main__":
    main(sys.argv)
