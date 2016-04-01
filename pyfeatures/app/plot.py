# BEGIN_COPYRIGHT
#
# Copyright (C) 2014-2016 CRS4.
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
Plot feature values across a given dimension.

Reads feature data from Avro containers output by 'pyfeatures calc'.

The '-f' option expects the name of a feature sub-vector, e.g.,
'haralick_textures'.
"""

import os
import sys
import errno
import cPickle
import shelve
import warnings
from contextlib import closing

import matplotlib.pyplot as plt

try:
    from pyavroc import AvroFileReader
except ImportError:
    from pyfeatures.pyavroc_emu import AvroFileReader
    warnings.warn("pyavroc not found, using standard avro lib\n")
from pyfeatures.feature_names import FEATURE_NAMES


AXES = "z", "c", "t"
AX_DESC = {
    "z": "Z-sections",
    "c": "Channels",
    "t": "Timepoints",
}
FV_NAMES = frozenset(_[0] for _ in FEATURE_NAMES.itervalues())


def iter_records(fn):
    ext = os.path.splitext(fn)[-1]
    if ext == ".db":
        with closing(shelve.open(fn, flag="r")) as shelf:
            for r in shelf.itervalues():
                yield r
    elif ext == ".pickle":
        with open(fn) as f:
            for r in cPickle.load(f):
                yield r
    else:
        with open(fn) as f:
            reader = AvroFileReader(f)
            for r in reader:
                yield r


def get_data(fn, axis, feature=None):
    other_axes = [_ for _ in AXES if _ != axis]
    data = {}
    for r in iter_records(fn):
        k1 = tuple(r[_] for _ in other_axes)
        k2 = (r['x'], r['y'])
        for name, idx in FEATURE_NAMES.itervalues():
            if feature and name != feature:
                continue
            k3 = (name, idx)
            data.setdefault(
                k1, {}).setdefault(
                    k2, {}).setdefault(
                        k3, []).append((r['t'], r[name][idx]))
    for k1, v1 in data.iteritems():
        for k2, v2 in v1.iteritems():
            for k3, v3 in v2.iteritems():
                v2[k3] = [_[1] for _ in sorted(v3)]
    return data


def plot_data(data, axis, out_dir, verbose=False):
    other_axes = [_ for _ in AXES if _ != axis]
    for k1, v1 in data.iteritems():
        if verbose:
            print "%r = %r" % (other_axes, k1)
        ax_tag = "%s%d_%s%d" % (other_axes[0], k1[0], other_axes[1], k1[1])
        for (x, y), v2 in v1.iteritems():
            if verbose:
                print "  (x, y) = (%d, %d)" % (x, y)
            xy_tag = "x%d_y%d" % (x, y)
            for (name, idx), feat_values in v2.iteritems():
                feat_tag = "%s_%d" % (name, idx)
                plt.close("all")
                fig, ax = plt.subplots()
                x = range(len(feat_values))
                ax.plot(x, feat_values)
                ax.set_xlabel(AX_DESC[axis])
                ax.set_ylabel(feat_tag)
                img_bn = "%s_%s_%s.png" % (ax_tag, xy_tag, feat_tag)
                fig.savefig(os.path.join(out_dir, img_bn))


def add_parser(subparsers):
    parser = subparsers.add_parser("plot", description=__doc__)
    parser.add_argument("in_fn", metavar="FEATURES_FILE",
                        help="Avro file containing feature data")
    parser.add_argument("axis", metavar="|".join(AXES), choices=AXES,
                        help="what to map to the horizontal axis in the plots")
    parser.add_argument("-f", "--feature", metavar="FEATURE", choices=FV_NAMES,
                        help="select only this feature (sub-vector)")
    parser.add_argument('-o', '--out-dir', metavar='DIR', default=os.getcwd())
    parser.add_argument('-v', '--verbose', action="store_true")
    parser.set_defaults(func=run)
    return parser


def run(args, extra_argv=None):
    try:
        os.makedirs(args.out_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            sys.exit('Cannot create output dir: %s' % e)
    if args.verbose:
        print "getting data..."
    data = get_data(args.in_fn, args.axis, feature=args.feature)
    plot_data(data, args.axis, args.out_dir, verbose=args.verbose)
