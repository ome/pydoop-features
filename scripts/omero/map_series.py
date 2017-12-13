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
Given an OMERO screen ID, map each series in each plate to the
corresponding well, field and image id.
"""

import sys
import argparse
import getpass
from string import uppercase as LETTERS
from operator import itemgetter

import omero
from omero.gateway import BlitzGateway

DEFAULT_USER = getpass.getuser()


def make_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('screen_id', metavar="SCREEN_ID", type=int)
    parser.add_argument("-H", "--host", metavar="HOST", default="localhost")
    parser.add_argument("-P", "--port", metavar="PORT", default=4064)
    parser.add_argument("-U", "--user", metavar="USER", default=DEFAULT_USER)
    parser.add_argument("-G", "--group", metavar="GROUP")
    parser.add_argument("-o", "--out-file", metavar="FILE", help="output file")
    return parser


def main(argv):
    parser = make_parser()
    args = parser.parse_args(argv[1:])
    if not args.out_file:
        args.out_file = "map_screen_%d.tsv" % args.screen_id
    passwd = getpass.getpass()
    client = omero.client(host=args.host, port=args.port)
    client.createSession(args.user, passwd)
    conn = BlitzGateway(client_obj=client)
    conn.SERVICE_OPTS.setOmeroGroup('-1')
    conn.setSecure(True)
    screen = conn.getObject("Screen", args.screen_id)
    print "writing to %s" % args.out_file
    print "SCREEN: %s" % screen.name
    with open(args.out_file, "w") as fo:
        fo.write("PLATE\tSERIES\tWELL\tFIELD\tImageID\tWellID\n")
        for p in screen.listChildren():
            rows = []
            print "  plate: %s" % p.name
            for w in p.listChildren():
                n_fields = sum(1 for _ in w.listChildren())
                for i in xrange(n_fields):
                    img = w.getImage(i)
                    well_tag = "%s%02d" % (LETTERS[w.row], w.column + 1)
                    rows.append((
                        p.name, img.getSeries(), well_tag, i + 1, img.id, w.id
                    ))
            rows.sort(key=itemgetter(1))
            rows.sort()
            for r in rows:
                fo.write("%s\t%d\t%s\t%d\t%d\t%d\n" % r)


if __name__ == "__main__":
    main(sys.argv)
