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

"""
Distributed image feature calculation with wnd-charm.
"""
import pydoop.mapreduce.api as api
import pydoop.mapreduce.pipes as pp
from pydoop.avrolib import AvroContext

from pyfeatures.bioimg import BioImgPlane
from pyfeatures.feature_calc import calc_features, to_avro


class Mapper(api.Mapper):

    def map(self, ctx):
        p = BioImgPlane(ctx.value)
        pixels = p.get_xy()
        plane_tag = '%s-z%04d-c%04d-t%04d' % (p.name, p.z, p.c, p.t)
        out_rec = to_avro(calc_features(pixels, plane_tag))
        out_rec['plane_tag'] = plane_tag
        ctx.emit(None, out_rec)


def __main__():
    pp.run_task(pp.Factory(mapper_class=Mapper), context_class=AvroContext)
