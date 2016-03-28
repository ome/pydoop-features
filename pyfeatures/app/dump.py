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
Dump the contents of an Avro container to a different format.

WARNING: the 'pickle' format tries to read the whole Avro container
into memory in order to dump it as a single list, so it's **not**
suitable for very large files.
"""

import cPickle
import os
import pprint
import warnings

try:
    from pyavroc import AvroFileReader
except ImportError:
    from pyfeatures.pyavroc_emu import AvroFileReader
    warnings.warn("pyavroc not found, using standard avro lib\n")


FORMATS = "pickle", "txt"


def iter_records(f, num_records=None):
    reader = AvroFileReader(f)
    for i, r in enumerate(reader):
        if num_records is not None and i >= num_records:
            raise StopIteration
        else:
            yield r


def write_records(records, fmt, out_fn):
    with open(out_fn, "w") as fo:
        if fmt == "pickle":
            cPickle.dump(list(records), fo, cPickle.HIGHEST_PROTOCOL)
        elif fmt == "txt":
            pp = pprint.PrettyPrinter(stream=fo)
            for r in records:
                pp.pprint(r)
        else:
            raise ValueError("Unknown output format: %r" % (fmt,))


def add_parser(subparsers):
    parser = subparsers.add_parser("dump", description=__doc__)
    parser.add_argument("in_fn", metavar="FILE", help="Avro container file")
    parser.add_argument('-n', '--num-records', type=int, metavar='INT',
                        help="number of records to output (default: all)")
    parser.add_argument('-o', '--out-fn', metavar='FILE', help="output file")
    parser.add_argument('-f', '--format', choices=FORMATS, default="txt",
                        metavar="|".join(FORMATS), help="output format")
    parser.set_defaults(func=run)
    return parser


def run(args, extra_argv=None):
    if not args.out_fn:
        tag = os.path.splitext(os.path.basename(args.in_fn))[0]
        args.out_fn = "%s.%s" % (tag, args.format)
    with open(args.in_fn) as f:
        records = iter_records(f, num_records=args.num_records)
        write_records(records, args.format, args.out_fn)
