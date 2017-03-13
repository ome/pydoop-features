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

"""
Quick and dirty script for converting CP results back to csv.
"""

import sys
import os

MR_OUT_DIR = sys.argv[1]

TAGS = 'IMAGE', 'CELLS', 'CYTOPLASM', 'NUCLEI'
OUTFS = dict((t, open('%s.csv' % t.title(), 'w')) for t in TAGS)
HEADER_WRITTEN = dict.fromkeys(TAGS, False)


def ser(row):
    return ','.join(row) + '\n'


ls = [_ for _ in os.listdir(MR_OUT_DIR) if not _.startswith('_')]
for bn in sorted(ls):
    fn = os.path.join(MR_OUT_DIR, bn)
    print 'reading from %s' % fn
    with open(fn) as f:
        for line in f:
            z, res = line.split('\t', 1)
            print '  z:', z
            z = int(z)
            res = eval(res)
            res['ImageNumber'] = str(z + 1)
            res['Group_Index'] = str(z + 1)
            for t in TAGS[1:]:
                print '  writing %s data' % t
                data = res.pop(t)
                for d in data:
                    d['ImageNumber'] = str(z + 1)
                    header, values = zip(*d.iteritems())
                    if not HEADER_WRITTEN[t]:
                        OUTFS[t].write(ser(header))
                        HEADER_WRITTEN[t] = True
                    OUTFS[t].write(ser(values))
            header, values = zip(*res.iteritems())
            if not HEADER_WRITTEN['IMAGE']:
                OUTFS['IMAGE'].write(ser(header))
                HEADER_WRITTEN['IMAGE'] = True
            OUTFS['IMAGE'].write(ser(values))

for f in OUTFS.itervalues():
    f.close()
