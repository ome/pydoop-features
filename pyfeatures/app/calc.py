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
Non-distributed feature calculation with WND-CHARM.

Read image planes from an Avro container created with the serialize
script (which runs it.crs4.features.ImageToAvro.java), compute feature
vectors with WND-CHARM and store them to an output Avro container.
"""

import sys
import os
import warnings
import errno
from argparse import ArgumentTypeError

try:
    from pyavroc import AvroFileReader, AvroFileWriter
except ImportError:
    from pyfeatures.pyavroc_emu import AvroFileReader, AvroFileWriter
    warnings.warn("pyavroc not found, using standard avro lib\n")

from pyfeatures.bioimg import BioImgPlane
from pyfeatures.feature_calc import calc_features, to_avro
from pyfeatures.schema import Signatures as out_schema


def get_image_size(fin):
    reader = AvroFileReader(fin)
    r = reader.next()
    size_map = dict(zip(r['dimension_order'], r['pixel_data']['shape']))
    return tuple(size_map[_] for _ in 'ZCT')


def get_subsets(args):
    def from_end_if_neg(sizei, i):
        if i < 0:
            return sizei + i
        return i

    # Getting the ZCT size is expensive, only fetch if necessary
    if any((i < 0) for i in
           args.zsubset.union(args.csubset).union(args.tsubset)):
        with open(args.in_fn) as fin:
            sizez, sizec, sizet = get_image_size(fin)
        zsubset = [from_end_if_neg(sizez, z) for z in args.zsubset]
        csubset = [from_end_if_neg(sizec, c) for c in args.csubset]
        tsubset = [from_end_if_neg(sizet, t) for t in args.tsubset]
    else:
        zsubset = args.zsubset
        csubset = args.csubset
        tsubset = args.tsubset
    return zsubset, csubset, tsubset


def run(logger, args, extra_argv=None):
    try:
        os.makedirs(args.out_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            sys.exit('Cannot create output dir: %s' % e)
    tag, ext = os.path.splitext(os.path.basename(args.in_fn))
    out_fn = os.path.join(args.out_dir, '%s_features%s' % (tag, ext))
    logger.info('writing to %s', out_fn)
    zsubset, csubset, tsubset = get_subsets(args)
    with open(out_fn, 'w') as fout:
        writer = AvroFileWriter(fout, out_schema)
        with open(args.in_fn) as fin:
            reader = AvroFileReader(fin)
            for r in reader:
                p = BioImgPlane(r)
                if zsubset and p.z not in zsubset:
                    continue
                if csubset and p.c not in csubset:
                    continue
                if tsubset and p.t not in tsubset:
                    continue
                pixels = p.get_xy()
                logger.info('processing %r', [p.z, p.c, p.t])
                kw = {
                    'long': args.long,
                    'w': args.width,
                    'h': args.height,
                    'dx': args.delta_x,
                    'dy': args.delta_y,
                    'ox': args.offset_x,
                    'oy': args.offset_y,
                }
                for fv in calc_features(pixels, p.name, **kw):
                    out_rec = to_avro(fv)
                    for name in 'img_path', 'series', 'z', 'c', 't':
                        out_rec[name] = getattr(p, name)
                    writer.write(out_rec)
        writer.close()
    return 0


def int_set(s):
    try:
        return set(int(_) for _ in s.split(","))
    except ValueError as e:
        raise ArgumentTypeError(e.message)


def add_parser(subparsers):
    parser = subparsers.add_parser("calc", description=__doc__)
    parser.add_argument('in_fn', metavar='AVRO_CONTAINER',
                        help='avro input file with serialized img planes')
    parser.add_argument('-o', '--out-dir', metavar='DIR', default=os.getcwd())
    parser.add_argument('-l', '--long', action='store_true',
                        help='extract WND-CHARM\'s "long" features set')
    parser.add_argument('-W', '--width', type=int, metavar="INT",
                        help='tile width (default = image width)')
    parser.add_argument('-H', '--height', type=int, metavar="INT",
                        help='tile height (default = image height)')
    parser.add_argument("-x", "--delta-x", type=int, metavar="INT",
                        help="horizontal distance between consecutive tiles")
    parser.add_argument("-y", "--delta-y", type=int, metavar="INT",
                        help="vertical distance between consecutive tiles")
    parser.add_argument("--offset-x", type=int, metavar="INT",
                        help="horizontal offset of first tile (default 0)")
    parser.add_argument("--offset-y", type=int, metavar="INT",
                        help="vertical offset of first tile (default 0)")
    parser.add_argument("-z", "--zsubset", type=int_set, metavar="INT,INT,...",
                        default=set(),
                        help="process only planes with these Z coordinates")
    parser.add_argument("-c", "--csubset", type=int_set, metavar="INT,INT,...",
                        default=set(),
                        help="process only planes with these C coordinates")
    parser.add_argument("-t", "--tsubset", type=int_set, metavar="INT,INT,...",
                        default=set(),
                        help="process only planes with these T coordinates")
    parser.set_defaults(func=run)
    return parser
