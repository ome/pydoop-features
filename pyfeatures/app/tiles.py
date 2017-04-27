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
Generate tiles according to the given parameters and output a
visual representation of the resulting coverage.
"""

import numpy as np

from pyfeatures.feature_calc import gen_tiles


IMG_ALPHA = 0.2
TILE_ALPHA = 0.3
MAX_SMALL_SIZE = 32


def add_parser(subparsers):
    parser = subparsers.add_parser("tiles", description=__doc__)
    parser.add_argument("iW", type=int, metavar="WIDTH", help="image width")
    parser.add_argument("iH", type=int, metavar="HEIGHT", help="image height")
    parser.add_argument("-W", type=int, metavar="INT", help="tile width")
    parser.add_argument("-H", type=int, metavar="INT", help="tile height")
    parser.add_argument("-x", type=int, metavar="INT", help="tile x-distance")
    parser.add_argument("-y", type=int, metavar="INT", help="tile y-distance")
    parser.add_argument("--offset-x", type=int, metavar="INT",
                        help="tile initial x-offset")
    parser.add_argument("--offset-y", type=int, metavar="INT",
                        help="tile initial y-offset")
    parser.add_argument('-o', '--out-fn', metavar='FILE', default="tiles.png",
                        help="output file (extension = img format)")
    parser.set_defaults(func=run)
    return parser


def run(logger, args, extra_argv=None):
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    img_array = np.zeros((args.iH, args.iW), dtype="i1")
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect='equal')
    ax.add_patch(patches.Rectangle((0, 0), args.iW, args.iH, alpha=IMG_ALPHA))
    mx = max(1, .05 * args.iW)
    my = max(1, .05 * args.iH)
    ax.axis([-mx, args.iW + mx, -my, args.iH + my])
    for i, j, tile in gen_tiles(img_array, w=args.W, h=args.H,
                                dx=args.x, dy=args.y,
                                ox=args.offset_x, oy=args.offset_y):
        h, w = tile.shape
        ax.add_patch(patches.Rectangle((j, i), w, h, alpha=TILE_ALPHA))
        logger.debug("%r", (j, i, w, h))
    ax.invert_yaxis()
    if max(args.iW, args.iH) <= MAX_SMALL_SIZE:
        ax.set_xticks(xrange(args.iW + 1))
        ax.set_yticks(xrange(args.iH + 1))
        ax.grid()
    logger.info("writing to %r" % (args.out_fn,))
    fig.savefig(args.out_fn)
