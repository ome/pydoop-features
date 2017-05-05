# BEGIN_COPYRIGHT
#
# Copyright (C) 2017 Open Microscopy Environment:
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
Summarize the contents of an output (featureset) Avro container.
"""

import os
import warnings

try:
    from pyavroc import AvroFileReader
except ImportError:
    from pyfeatures.pyavroc_emu import AvroFileReader
    warnings.warn("pyavroc not found, using standard avro lib\n")


def add_parser(subparsers):
    parser = subparsers.add_parser("summarize", description=__doc__)
    parser.add_argument("in_fn", metavar="FILE", help="Avro container file")
    parser.add_argument("-o", "--out-fn", metavar="FILE", help="output file")
    parser.set_defaults(func=run)
    return parser


def run(logger, args, extra_argv=None):
    if not args.out_fn:
        tag = os.path.splitext(os.path.basename(args.in_fn))[0]
        args.out_fn = "%s.summary" % tag
    str_keys = ["name", "img_path"]
    int_keys = ["series", "z", "c", "t", "w", "h", "x", "y"]
    d = {"n_features": set()}
    with open(args.in_fn) as f:
        reader = AvroFileReader(f)
        for r in reader:
            d["n_features"].add(
                sum(len(v) for k, v in r.iteritems() if type(v) is list)
            )
            for k in str_keys:
                d.setdefault(k, set()).add(r[k])
            for k in int_keys:
                d.setdefault(k, set()).add(int(r[k]))
    logger.info("writing to %s", args.out_fn)
    with open(args.out_fn, "w") as fo:
        for k in str_keys:
            fo.write("%s: %s\n" % (k, ", ".join(sorted(d[k]))))
        for k in int_keys:
            v = sorted(d[k])
            if len(v) > 2 and v == range(v[0], v[-1] + 1):
                fo.write("%s: %d-%d\n" % (k, v[0], v[-1]))
            else:
                fo.write("%s: %s\n" % (k, ", ".join(map(str, v))))
