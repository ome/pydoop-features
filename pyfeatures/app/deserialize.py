# BEGIN_COPYRIGHT
#
# Copyright (C) 2014-2017 Open Microscopy Environment:
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
Deserialize BioImgPlane records.
"""

import sys
import os
import warnings
from contextlib import closing
import errno

try:
    from pyavroc import AvroFileReader
except ImportError:
    from pyfeatures.pyavroc_emu import AvroFileReader
    warnings.warn("pyavroc not found, using standard avro lib\n")
import numpy as np
from libtiff import TIFF

from pyfeatures.bioimg import BioImgPlane


# no schema needed for deserialization
def iterplanes(avro_file):
    with open(avro_file, 'rb') as f:
        reader = AvroFileReader(f)
        for r in reader:
            yield BioImgPlane(r)


def run(logger, args, extra_argv=None):
    try:
        os.makedirs(args.out_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            sys.exit('Cannot create output dir: %s' % e)
    for p in iterplanes(args.avro_file):
        pixels = p.get_xy()
        out_tag = '%s-z%04d-c%04d-t%04d' % (p.name, p.z, p.c, p.t)
        logger.info("writing plane %s", out_tag)
        if args.img:
            out_fn = os.path.join(args.out_dir, '%s.tif' % out_tag)
            with closing(TIFF.open(out_fn, mode="w")) as fo:
                fo.write_image(pixels)
        else:
            out_fn = os.path.join(args.out_dir, '%s.npy' % out_tag)
            np.save(out_fn, pixels)
    return 0


def add_parser(subparsers):
    parser = subparsers.add_parser("deserialize", description=__doc__)
    parser.add_argument('avro_file', metavar='AVRO_FILE')
    parser.add_argument('out_dir', metavar='OUT_DIR')
    parser.add_argument('--img', action='store_true',
                        help='write images instead of .npy dumps')
    parser.set_defaults(func=run)
    return parser
