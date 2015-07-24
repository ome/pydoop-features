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
Minimal CP example.
"""

import os

import Image

import pydoop.mapreduce.api as api
import pydoop.mapreduce.pipes as pp
from pydoop.avrolib import AvroContext

from bioimg import BioImgPlane

# --- FIXME: the following info should be extracted from the pipeline file
CHANNEL_TAGS = ['D.TIF', 'F.TIF', 'R.TIF']
SET_SIZE = len(CHANNEL_TAGS)
#-------------------------------------------------------------------------


class Mapper(api.Mapper):

    def __init__(self, ctx):
        super(Mapper, self).__init__(ctx)
        self.img_set = []
        self.cwd = os.getcwd()
        self.ctx = ctx

    def map(self, ctx):
        p = BioImgPlane(ctx.value)
        if len(self.img_set) >= SET_SIZE:
            self.__process_current_set(ctx)
            self.img_set = []
        self.img_set.append(p)

    def __process_current_set(self, ctx):
        img_list = []
        for p, tag in zip(self.img_set, CHANNEL_TAGS):
            pixels = p.get_xy()
            pixels = pixels.reshape(pixels.shape[1], pixels.shape[0])
            im = Image.fromarray(pixels)
            out_fn = 'z%04d_%s' % (p.z, tag)
            im.save(out_fn)
            img_list.append(os.path.join(self.cwd, out_fn))
            # TODO: run cp on these files
        ctx.emit(str(p.z), ', '.join(img_list))

    def close(self):
        self.__process_current_set(self.ctx)


def __main__():
    pp.run_task(pp.Factory(mapper_class=Mapper), context_class=AvroContext)
