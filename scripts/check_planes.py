# BEGIN_COPYRIGHT
#
# Copyright (C) 2015-2017 Open Microscopy Environment:
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
Quick hack to compare .npy img plane dumps.

Expected file name structure: <PREFIX>-z<Z_INDEX>-c<C_INDEX>-t<T_INDEX>.npy
where indices are 0-padded to 4 digits, e.g., foo-z0022-c0001-t0000.npy
"""

import sys
import os
import glob
import re

import numpy as np


FN_PATTERN = re.compile(r'^[^-]+-z(\d+)-c(\d+)-t(\d+).npy$')


def get_zct_max(prefix):
    triples = []
    for fn in glob.glob('%s*' % prefix):
        bn = os.path.basename(fn)
        triples.append(map(int, FN_PATTERN.match(bn).groups()))
    zs, cs, ts = zip(*triples)
    return max(zs), max(cs), max(ts)


try:
    prefix_a = sys.argv[1]
    prefix_b = sys.argv[2]
except IndexError:
    sys.exit("Usage: %s PREFIX_A PREFIX_B\n%s" % (sys.argv[0], __doc__))

z_max, c_max, t_max = get_zct_max(prefix_a)
if get_zct_max(prefix_b) != (z_max, c_max, t_max):
    sys.exit("ERROR: different file structure for the two prefixes")
for z in xrange(z_max + 1):
    for c in xrange(c_max + 1):
        for t in xrange(t_max + 1):
            fnames = ['%s-z%04d-c%04d-t%04d.npy' % (_, z, c, t)
                      for _ in prefix_a, prefix_b]
            print z, c, t,
            sys.stdout.flush()
            try:
                a, b = [np.load(_) for _ in fnames]
            except IOError as e:
                print 'ERROR: %s' % e
            else:
                print 'OK' if np.array_equal(a, b) else 'ERROR: arrays differ'
