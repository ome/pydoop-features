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

import wndcharm
from wndcharm.FeatureVector import FeatureVector
from pychrm.PyImageMatrix import PyImageMatrix

import pydoop.mapreduce.api as api
import pydoop.mapreduce.pipes as pp
from pydoop.avrolib import AvroContext

from bioimg import BioImgPlane


def calc_features(img_arr, plane_tag):
    assert len(img_arr.shape) == 2
    pychrm_matrix = PyImageMatrix()
    pychrm_matrix.allocate(img_arr.shape[1], img_arr.shape[0])
    numpy_matrix = pychrm_matrix.as_ndarray()
    numpy_matrix[:] = img_arr
    signatures = FeatureVector(basename=plane_tag)
    signatures.original_px_plane = pychrm_matrix
    signatures.GenerateFeatures()
    return signatures

def to_avro(signatures):
    try:
        rec = {'feature_names': signatures.feature_names, 'values': signatures.values}
    except AttributeError:
        raise RuntimeError('signatures obj must have feature_names and values attrs')
    for k in ('name', 'feature_set_version', 'source_filepath', 'auxiliary_feature_storage'):
        try:
            rec[k] = getattr(signatures, k)
        except AttributeError:
            pass
    return rec


class Mapper(api.Mapper):

    def map(self, ctx):
        p = BioImgPlane(ctx.value)
        pixels = p.get_xy()
        plane_tag = '%s-z%04d-c%04d-t%04d' % (p.name, p.z, p.c, p.t)
        out_rec = to_avro(plane_tag, calc_features(pixels, plane_tag))
        out_rec['plane_tag'] = plane_tag
        ctx.emit(None, out_rec)


def __main__():
    pp.run_task(pp.Factory(mapper_class=Mapper), context_class=AvroContext)
