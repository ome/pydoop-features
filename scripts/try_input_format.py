#!/usr/bin/env python

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

import numpy as np

import pydoop.mapreduce.api as api
import pydoop.mapreduce.pipes as pp
from pydoop.avrolib import AvroContext
import pydoop.hdfs as hdfs

from pyfeatures.bioimg import BioImgPlane


DUMP_DIR = 'bioimg.dump.dir'
HDFS_USER = 'pydoop.hdfs.user'


class Mapper(api.Mapper):

    def __init__(self, ctx):
        jc = ctx.job_conf
        self.out_dir = jc.get(DUMP_DIR, 'planes_dump')
        self.hdfs_user = jc.get(HDFS_USER, None)

    def map(self, ctx):
        p = BioImgPlane(ctx.value)
        pixels = p.get_xy()
        bn = '%s-z%04d-c%04d-t%04d.npy' % (p.name, p.z, p.c, p.t)
        fn = hdfs.path.join(self.out_dir, p.name, bn)
        with hdfs.open(fn, 'w') as fo:
            np.save(fo, pixels)
        ctx.emit(fn, '%s\t%s' % (p.dimension_order, pixels.shape))


def __main__():
    pp.run_task(pp.Factory(mapper_class=Mapper), context_class=AvroContext)
