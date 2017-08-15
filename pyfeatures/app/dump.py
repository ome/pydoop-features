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
Dump the contents of an Avro container to a different format.

WARNING: the 'pickle' and 'json' formats read the whole Avro container
into memory in order to dump it as a single list, so they're **not**
suitable for very large files.
"""

import cPickle
import json
import os
import pprint
import shelve
import warnings
from contextlib import closing

try:
    from pyavroc import AvroFileReader
except ImportError:
    from pyfeatures.pyavroc_emu import AvroFileReader
    warnings.warn("pyavroc not found, using standard avro lib\n")


FORMATS = "db", "pickle", "txt", "json"
PROTOCOL = cPickle.HIGHEST_PROTOCOL


def iter_records(f, logger, num_records=None):
    reader = AvroFileReader(f)
    for i, r in enumerate(reader):
        logger.debug("record #%d", i)
        if num_records is not None and i >= num_records:
            raise StopIteration
        else:
            yield r


class Writer(object):

    def __init__(self, fmt, out_fn):
        if fmt not in FORMATS:
            raise ValueError("Unknown output format: %r" % (fmt,))
        self.fmt = fmt
        self.out_fn = out_fn

    def write(self, records):
        getattr(self, "_write_%s" % self.fmt)(records)

    def _write_db(self, records):
        try:
            os.remove(self.out_fn)  # shelve.open does not overwrite
        except OSError:
            pass
        with closing(
            shelve.open(self.out_fn, flag="n", protocol=PROTOCOL)
        ) as shelf:
            for i, r in enumerate(records):
                shelf[str(i)] = r

    def _write_pickle(self, records):
        with open(self.out_fn, "w") as fo:
            cPickle.dump(list(records), fo, PROTOCOL)

    def _write_txt(self, records):
        with open(self.out_fn, "w") as fo:
            pp = pprint.PrettyPrinter(stream=fo)
            for r in records:
                pp.pprint(r)

    def _write_json(self, records):
        with open(self.out_fn, "w") as fo:
            json.dump(list(records), fo,
                      sort_keys=True, indent=1, separators=(',', ': '))


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


def run(logger, args, extra_argv=None):
    if not args.out_fn:
        tag = os.path.splitext(os.path.basename(args.in_fn))[0]
        args.out_fn = "%s.%s" % (tag, args.format)
    logger.info("writing to %s", args.out_fn)
    with open(args.in_fn) as f:
        records = iter_records(f, logger, num_records=args.num_records)
        Writer(args.format, args.out_fn).write(records)
