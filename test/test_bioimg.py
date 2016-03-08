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

import unittest
import operator
import numpy as np

import pyfeatures.bioimg as bioimg


def make_random_values(dtype, size):
    try:
        info = np.iinfo(dtype)
    except ValueError:
        info = np.finfo(dtype)
        x = np.random.ranf(size)
        return (x - .5) * info.max * 2  # info.max - info.min overflows
    else:
        return np.random.randint(info.min, info.max, size)


def make_random_array(dtype, deltas):
    rv = make_random_values(dtype, reduce(operator.mul, deltas))
    return rv.astype(dtype).reshape(tuple(deltas))


class TestArraySlice(unittest.TestCase):

    def setUp(self):
        self.cases = [
            # little_endian should make no difference for {U,}INT8
            {"dtype": "INT8", "little_endian": False, "np_dtype": ">i1"},
            {"dtype": "INT8", "little_endian": True, "np_dtype": "<i1"},
            {"dtype": "UINT8", "little_endian": False, "np_dtype": ">u1"},
            {"dtype": "UINT8", "little_endian": True, "np_dtype": "<u1"},
            {"dtype": "INT16", "little_endian": False, "np_dtype": ">i2"},
            {"dtype": "INT16", "little_endian": True, "np_dtype": "<i2"},
            {"dtype": "UINT16", "little_endian": False, "np_dtype": ">u2"},
            {"dtype": "UINT16", "little_endian": True, "np_dtype": "<u2"},
            {"dtype": "INT32", "little_endian": False, "np_dtype": ">i4"},
            {"dtype": "INT32", "little_endian": True, "np_dtype": "<i4"},
            {"dtype": "UINT32", "little_endian": False, "np_dtype": ">u4"},
            {"dtype": "UINT32", "little_endian": True, "np_dtype": "<u4"},
            {"dtype": "FLOAT32", "little_endian": False, "np_dtype": ">f4"},
            {"dtype": "FLOAT32", "little_endian": True, "np_dtype": "<f4"},
            {"dtype": "FLOAT64", "little_endian": False, "np_dtype": ">f8"},
            {"dtype": "FLOAT64", "little_endian": True, "np_dtype": "<f8"},
        ]
        self.shape = [32, 16, 2, 3, 4]
        self.offsets = [4, 8, 1, 2, 1]
        self.deltas = [10, 6, 1, 1, 2]

    def runTest(self):
        record = {
            "shape": self.shape,
            "offsets": self.offsets,
            "deltas": self.deltas,
        }
        for c in self.cases:
            record["dtype"] = c["dtype"]
            record["little_endian"] = c["little_endian"]
            a = make_random_array(c["np_dtype"], self.deltas)
            record["data"] = a.tostring()
            sl = bioimg.ArraySlice(record)
            self.assertEqual(sl.shape, self.shape)
            self.assertEqual(sl.offsets, self.offsets)
            self.assertEqual(sl.deltas, self.deltas)
            self.assertTrue(np.array_equal(sl.data, a))


class TestBioImgPlane(TestArraySlice):

    def setUp(self):
        super(TestBioImgPlane, self).setUp()
        c = self.cases[0]
        self.pixel_data = {
            "shape": self.shape,
            "offsets": self.offsets,
            "deltas": self.deltas,  # not a single plane, exception expected
            "dtype": c["dtype"],
            "little_endian": c["little_endian"],
            "data": make_random_array(c["np_dtype"], self.deltas).tostring(),
        }
        self.record = {
            "name": "foo",
            "dimension_order": "XYTZC",
            "pixel_data": self.pixel_data,
        }
        self.np_dtype = c["np_dtype"]
        self.zct = dict(zip(
            self.record["dimension_order"][2:], self.offsets[2:]
        ))

    def runTest(self):
        self.assertRaises(ValueError, bioimg.BioImgPlane, self.record)
        deltas = self.record["pixel_data"]["deltas"]
        deltas[-1] = 1
        self.record["pixel_data"]["data"] = make_random_array(
            self.np_dtype, deltas
        ).tostring()
        plane = bioimg.BioImgPlane(self.record)
        self.assertEqual(plane.name, self.record["name"])
        self.assertEqual(plane.dimension_order, self.record["dimension_order"])
        self.assertEqual(plane.z, self.zct["Z"])
        self.assertEqual(plane.c, self.zct["C"])
        self.assertEqual(plane.t, self.zct["T"])


def load_tests(loader, tests, pattern):
    test_cases = (TestArraySlice, TestBioImgPlane)
    suite = unittest.TestSuite()
    for tc in test_cases:
        suite.addTests(loader.loadTestsFromTestCase(tc))
    return suite


def main():
    suite = load_tests(unittest.defaultTestLoader, None, None)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == '__main__':
    main()
