# BEGIN_COPYRIGHT
#
# Copyright (C) 2014-2015 CRS4.
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
Pydoop script for image feature calculation.
"""
import numpy as np

import pydoop.hdfs as hdfs
import pydoop.utils as utils


def get_array(path, user=None):
    with hdfs.open(path, user=user) as f:
        return np.load(f)


def calc_features(img_arr):
    # FIXME: dummy
    return np.random.random(img_arr.shape)


def mapper(_, record, writer, conf):
    out_dir = conf.get('out.dir', utils.make_random_str())
    user = conf.get('hdfs.user', '')
    hdfs.mkdir(out_dir, user='')  # does nothing if out_dir already exists
    img_path = record.strip()
    a = get_array(img_path)
    out_a = calc_features(a)
    out_path = hdfs.path.join(out_dir, '%s.out' % hdfs.path.basename(img_path))
    with hdfs.open(out_path, 'w', user=user) as fo:
        np.save(fo, out_a)  # actual output
    writer.emit(img_path, fo.name)  # info (tab-separated input-output)
