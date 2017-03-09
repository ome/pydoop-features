# BEGIN_COPYRIGHT
#
# Copyright (C) 2016-2017 Open Microscopy Environment:
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

from itertools import izip

from wndcharm.FeatureVector import FeatureVector
from wndcharm.PyImageMatrix import PyImageMatrix

from pyfeatures.feature_names import FEATURE_NAMES


def get_image_matrix(img_array):
    if len(img_array.shape) != 2:
        raise ValueError("array must be two-dimensional")
    image_matrix = PyImageMatrix()
    image_matrix.allocate(img_array.shape[1], img_array.shape[0])
    numpy_matrix = image_matrix.as_ndarray()
    numpy_matrix[:] = img_array
    return image_matrix


def gen_tiles(img_array, w=None, h=None, dx=None, dy=None):
    if len(img_array.shape) != 2:
        raise ValueError("array must be two-dimensional")
    H, W = img_array.shape
    if w is None or w > W:
        w = W
    if h is None or h > H:
        h = H
    if dx is None:
        dx = w
    if dy is None:
        dy = h
    if w < 1 or h < 1:
        raise ValueError("smallest tile size is 1 x 1")
    if dx < 1 or dy < 1:
        raise ValueError("smallest distance between tiles is 1")
    for i in xrange(0, min(H, H - h + dy), dy):
        for j in xrange(0, min(W, W - w + dx), dx):
            yield i, j, img_array[i: i + h, j: j + w]


def calc_features(img_array, tag, long=False, w=None, h=None,
                  dx=None, dy=None):
    if len(img_array.shape) != 2:
        raise ValueError("array must be two-dimensional")
    for i, j, tile in gen_tiles(img_array, w=w, h=h, dx=dx, dy=dy):
        signatures = FeatureVector(basename=tag, long=long)
        signatures.original_px_plane = get_image_matrix(tile)
        signatures.GenerateFeatures(write_to_disk=False)
        signatures.x, signatures.y = j, i
        signatures.h, signatures.w = tile.shape
        yield signatures


def to_avro(signatures):
    rec = dict((_[0], []) for _ in FEATURE_NAMES.itervalues())
    for fname, value in izip(signatures.feature_names, signatures.values):
        vname, idx = FEATURE_NAMES[fname]
        rec[vname].append((idx, value))
    for vname, tuples in rec.iteritems():
        rec[vname] = [_[1] for _ in sorted(tuples)]
    rec["version"] = signatures.feature_set_version
    rec["name"] = signatures.basename
    for k in "x", "y", "w", "h":
        rec[k] = getattr(signatures, k)
    return rec
