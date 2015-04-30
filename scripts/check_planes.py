"""
Quick hack to compare .npy img plane dumps.

Expected file name structure: <PREFIX>-z<Z_INDEX>-c<C_INDEX>-t<T_INDEX>.npy
where indices are 0-padded to 4 digits, e.g., foo-z0022-c0001-t0000.npy
"""

import sys
import numpy as np

try:
    prefix_a = sys.argv[1]
    prefix_b = sys.argv[2]
    z_max = int(sys.argv[3])
    c_max = int(sys.argv[4])
    t_max = int(sys.argv[5])
except IndexError:
    sys.exit("Usage: %s PREFIX_A PREFIX_B Z_MAX C_MAX T_MAX\n%s" % (
        sys.argv[0], __doc__
    ))

for z in xrange(z_max):
    for c in xrange(c_max):
        for t in xrange(t_max):
            fnames = ['%s-z%04d-c%04d-t%04d.npy' % (_, z, c, t)
                      for _ in prefix_a, prefix_b]
            print z, c, t,
            try:
                a, b = [np.load(_) for _ in fnames]
            except IOError as e:
                print 'ERROR: %s' % e
            else:
                print 'OK' if np.array_equal(a, b) else 'ERROR: arrays differ'
