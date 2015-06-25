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
Distributed image feature calculation with wnd-charm.
"""

import re

import pychrm
from pychrm.FeatureSet import Signatures
from pychrm.PyImageMatrix import PyImageMatrix

import pydoop.mapreduce.api as api
import pydoop.mapreduce.pipes as pp
from pydoop.avrolib import AvroContext

from bioimg import BioImgPlane


def calc_features(img_arr):
    assert len(img_arr.shape) == 2
    pychrm_matrix = PyImageMatrix()
    pychrm_matrix.allocate(img_arr.shape[1], img_arr.shape[0])
    numpy_matrix = pychrm_matrix.as_ndarray()
    numpy_matrix[:] = img_arr
    feature_plan = pychrm.StdFeatureComputationPlans.getFeatureSet()
    wnd_charm_options = ""
    fts = Signatures.NewFromFeatureComputationPlan(
        pychrm_matrix, feature_plan, wnd_charm_options
    )
    return fts.values


class Mapper(api.Mapper):

    def map(self, ctx):
        p = BioImgPlane(ctx.value)
        pixels = p.get_xy()
        tag = '%s-z%04d-c%04d-t%04d.npy' % (p.name, p.z, p.c, p.t)
        features = calc_features(pixels)
        ctx.emit(tag, re.sub('\s+', ' ', repr(features)))


def __main__():
    pp.run_task(pp.Factory(mapper_class=Mapper), context_class=AvroContext)
