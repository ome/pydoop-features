# BEGIN_COPYRIGHT
#
# Copyright (C) 2014-2015 CRS4.
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

# TODO: move this code to a package

import itertools
import operator

import numpy as np


class ArraySlice(object):

    def __init__(self, avro_record):
        r = avro_record
        if not r['little_endian']:
            raise RuntimeError('big endian data not supported (yet)')
        self.shape = r['shape']
        self.offsets = r['offsets']
        self.deltas = r['deltas']
        self.__check_boundaries()
        dtype = getattr(np, r['dtype'].lower())
        self.__check_size(r['data'], dtype)
        self.data = np.fromstring(r['data'], dtype=dtype).reshape(r['deltas'])

    def __check_boundaries(self):
        n_dim = len(self.shape)
        if not (len(self.offsets) == len(self.deltas) == n_dim):
            raise ValueError('shape/offsets/deltas must have the same length')
        for s, o, d in itertools.izip(self.shape, self.offsets, self.deltas):
            if not (0 <= o <= o + d <= s):
                raise ValueError(
                    '0 <= %d <= %d + %d <= %d is false' % (o, o + d, s)
                )

    def __check_size(self, data, dtype):
        n_elements = reduce(operator.mul, self.deltas)
        expected_size = n_elements * dtype().nbytes
        if len(data) != expected_size:
            raise ValueError(
                'unexpected data size (%d != %d)' % (len(data), expected_size)
            )


class BioImgPlane(object):

    BASE_DIM_ORDER = 'XYZCT'

    def __init__(self, avro_record):
        r = avro_record
        self.name = r['name']
        self.dimension_order = r['dimension_order']
        self.__check_dim_order()
        self.indices = [
            self.dimension_order.index(_) for _ in self.BASE_DIM_ORDER
        ]  # FIXME: optimize this
        self.i_x, self.i_y, self.i_z, self.i_c, self.i_t = self.indices
        self.pixel_data = ArraySlice(r['pixel_data'])
        self.__check_is_plane()
        self.z = self.pixel_data.offsets[self.i_z]
        self.c = self.pixel_data.offsets[self.i_c]
        self.t = self.pixel_data.offsets[self.i_t]

    def __check_dim_order(self):
        if (len(self.dimension_order) != len(self.BASE_DIM_ORDER) or
            set(self.dimension_order) != set(self.BASE_DIM_ORDER)):
            raise ValueError('dimension order must be a permutation of %r' %
                             self.BASE_DIM_ORDER)

    def __check_is_plane(self):
        dz, dt, dc = [self.pixel_data.deltas[_] for _ in self.indices[2:]]
        if not(dz == dt == dc == 1):
            raise ValueError('data is not flat along the zct dimensions')

    def get_xy(self):
        idx = [None] * len(self.dimension_order)
        for i in self.indices[2:]:
            idx[i] = 0
        idx[self.i_x] = slice(0, self.pixel_data.shape[self.i_x])
        idx[self.i_y] = slice(0, self.pixel_data.shape[self.i_y])
        return self.pixel_data.data[tuple(idx)]
