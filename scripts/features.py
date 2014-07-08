# BEGIN_COPYRIGHT
#
# Copyright (C) 2014 CRS4.
#
# This file is part of pydoop-features.
#
# pydoop-features is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# pydoop-features is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pydoop-features.  If not, see <http://www.gnu.org/licenses/>.
#
# END_COPYRIGHT

"""
Pydoop script for image feature calculation.
"""
import numpy as np

import pydoop.hdfs as hdfs
import pydoop.utils as utils


def get_array(path):
    with hdfs.open(path) as f:
        return np.load(f)


def calc_features(img_arr):
    # FIXME: dummy
    return np.random.random(img_arr.shape)


def mapper(_, record, writer, conf):
    out_dir = conf.get('out.dir', utils.make_random_str())
    hdfs.mkdir(out_dir)  # does nothing if out_dir already exists
    img_path = record.strip()
    a = get_array(img_path)
    out_a = calc_features(a)
    out_path = hdfs.path.join(out_dir, '%s.out' % hdfs.path.basename(img_path))
    with hdfs.open(out_path, 'w') as fo:
        np.save(fo, out_a)  # actual output
    writer.emit(img_path, fo.name)  # info (tab-separated input-output)
