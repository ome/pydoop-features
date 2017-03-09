# BEGIN_COPYRIGHT
#
# Copyright (C) 2014-2017 CRS4.
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
import tempfile
import shutil
import os
from contextlib import closing
from itertools import izip

import numpy as np
from libtiff import TIFF
from avro.schema import AvroException
from wndcharm.FeatureVector import FeatureVector

from pyfeatures.feature_calc import gen_tiles, calc_features, to_avro
from pyfeatures.feature_names import FEATURE_NAMES
import pyfeatures.pyavroc_emu as pyavroc_emu
from pyfeatures.schema import Signatures


W, H = 8, 6
DTYPE = np.uint8


def make_random_data():
    info = np.iinfo(DTYPE)
    a = np.random.randint(
        info.min, info.max, W * H
    ).astype(DTYPE).reshape((H, W))
    return a


def dump_to_tiff(ndarray, filename):
    with closing(TIFF.open(filename, mode="w")) as fo:
        fo.write_image(ndarray)


class TestGenTiles(unittest.TestCase):

    def setUp(self):
        self.a = np.arange(H * W).reshape((H, W))
        self.cases = [
            ({'w': 3, 'h': None, 'dx': 1, 'dy': None},
             [(0, 6, 0, 3), (0, 6, 1, 4), (0, 6, 2, 5),
              (0, 6, 3, 6), (0, 6, 4, 7), (0, 6, 5, 8)]),
            ({'w': 3, 'h': None, 'dx': 2, 'dy': None},
             [(0, 6, 0, 3), (0, 6, 2, 5), (0, 6, 4, 7), (0, 6, 6, 8)]),
            ({'w': 3, 'h': None, 'dx': 3, 'dy': None},
             [(0, 6, 0, 3), (0, 6, 3, 6), (0, 6, 6, 8)]),
            ({'w': 3, 'h': None, 'dx': 4, 'dy': None},
             [(0, 6, 0, 3), (0, 6, 4, 7)]),
            ({'w': 3, 'h': None, 'dx': 5, 'dy': None},
             [(0, 6, 0, 3), (0, 6, 5, 8)]),
            ({'w': 3, 'h': None, 'dx': 6, 'dy': None},
             [(0, 6, 0, 3), (0, 6, 6, 8)]),
            ({'w': 3, 'h': None, 'dx': 7, 'dy': None},
             [(0, 6, 0, 3), (0, 6, 7, 8)]),
            ({'w': 3, 'h': None, 'dx': 8, 'dy': None},
             [(0, 6, 0, 3)]),
            ({'w': 3, 'h': None, 'dx': 100, 'dy': None},
             [(0, 6, 0, 3)]),
            # --
            ({'w': None, 'h': 3, 'dx': None, 'dy': 1},
             [(0, 3, 0, 8), (1, 4, 0, 8), (2, 5, 0, 8), (3, 6, 0, 8)]),
            ({'w': None, 'h': 3, 'dx': None, 'dy': 2},
             [(0, 3, 0, 8), (2, 5, 0, 8), (4, 6, 0, 8)]),
            ({'w': None, 'h': 3, 'dx': None, 'dy': 3},
             [(0, 3, 0, 8), (3, 6, 0, 8)]),
            ({'w': None, 'h': 3, 'dx': None, 'dy': 4},
             [(0, 3, 0, 8), (4, 6, 0, 8)]),
            ({'w': None, 'h': 3, 'dx': None, 'dy': 5},
             [(0, 3, 0, 8), (5, 6, 0, 8)]),
            ({'w': None, 'h': 3, 'dx': None, 'dy': 6},
             [(0, 3, 0, 8)]),
            ({'w': None, 'h': 3, 'dx': None, 'dy': 100},
             [(0, 3, 0, 8)]),
        ]

    def runTest(self):
        for kwargs, slices in self.cases:
            tiles = list(gen_tiles(self.a, **kwargs))
            self.assertEqual(len(tiles), len(slices))
            for (i, j, t), (i1, i2, j1, j2) in izip(tiles, slices):
                self.assertTrue(np.array_equal(t, self.a[i1: i2, j1: j2]))


class Base(unittest.TestCase):

    def setUp(self):
        self.name = "img_0"
        self.img_path = "/foo/img_0.tif"
        self.series = 0
        self.z = self.c = self.t = 0


class TestFeatureCalc(Base):

    def setUp(self):
        super(TestFeatureCalc, self).setUp()
        self.wd = tempfile.mkdtemp(prefix="pyfeatures_")

    def tearDown(self):
        shutil.rmtree(self.wd)

    def test_no_tiling(self):
        a = make_random_data()
        for long in False, True:
            all_sigs = list(calc_features(a, self.name, long=long))
            self.assertEqual(len(all_sigs), 1)
            sigs = all_sigs[0]
            self.assertEqual((sigs.x, sigs.y, sigs.w, sigs.h), (0, 0, W, H))
            exp_sigs = self.__get_exp_features(a, long=long)
            self.assertFeaturesEqual(sigs, exp_sigs)

    def test_tiling(self):
        a = make_random_data()
        w, h = 3, 4
        s = list(calc_features(a, self.name, w=w, h=h))
        self.assertEqual(len(s), 6)
        self.assertEqual((s[0].x, s[0].y, s[0].w, s[0].h), (0, 0, 3, 4))
        self.assertFeaturesEqual(s[0], self.__get_exp_features(a[:4, :3]))
        self.assertEqual((s[1].x, s[1].y, s[1].w, s[1].h), (3, 0, 3, 4))
        self.assertFeaturesEqual(s[1], self.__get_exp_features(a[:4, 3:6]))
        self.assertEqual((s[2].x, s[2].y, s[2].w, s[2].h), (6, 0, 2, 4))
        self.assertFeaturesEqual(s[2], self.__get_exp_features(a[:4, 6:]))
        self.assertEqual((s[3].x, s[3].y, s[3].w, s[3].h), (0, 4, 3, 2))
        self.assertFeaturesEqual(s[3], self.__get_exp_features(a[4:, :3]))
        self.assertEqual((s[4].x, s[4].y, s[4].w, s[4].h), (3, 4, 3, 2))
        self.assertFeaturesEqual(s[4], self.__get_exp_features(a[4:, 3:6]))
        self.assertEqual((s[5].x, s[5].y, s[5].w, s[5].h), (6, 4, 2, 2))
        self.assertFeaturesEqual(s[5], self.__get_exp_features(a[4:, 6:]))

    def test_tiling_dist(self):
        a = make_random_data()
        w, h = 5, 2
        dx, dy = 3, 3
        s = list(calc_features(a, self.name, w=w, h=h, dx=dx, dy=dy))
        self.assertEqual(len(s), 4)
        self.assertEqual((s[0].x, s[0].y, s[0].w, s[0].h), (0, 0, 5, 2))
        self.assertFeaturesEqual(s[0], self.__get_exp_features(a[:2, :5]))
        self.assertEqual((s[1].x, s[1].y, s[1].w, s[1].h), (3, 0, 5, 2))
        self.assertFeaturesEqual(s[1], self.__get_exp_features(a[:2, 3:]))
        self.assertEqual((s[2].x, s[2].y, s[2].w, s[2].h), (0, 3, 5, 2))
        self.assertFeaturesEqual(s[2], self.__get_exp_features(a[3:5, :5]))
        self.assertEqual((s[3].x, s[3].y, s[3].w, s[3].h), (3, 3, 5, 2))
        self.assertFeaturesEqual(s[3], self.__get_exp_features(a[3:5, 3:]))

    def assertFeaturesEqual(self, fv1, fv2):
        for name in "feature_names", "feature_set_version":
            self.assertEquals(getattr(fv1, name), getattr(fv2, name))
        for v1, v2 in izip(fv1.values, fv2.values):
            self.assertAlmostEquals(v1, v2)

    def __get_exp_features(self, a, long=False):
        fn = os.path.join(self.wd, "img.tiff")
        dump_to_tiff(a, fn)
        fv = FeatureVector(source_filepath=fn, long=long)
        return fv.GenerateFeatures(write_to_disk=False)


class TestToAvro(Base):

    def setUp(self):
        super(TestToAvro, self).setUp()

    def test_no_tiling(self):
        a = make_random_data()
        for long in False, True:
            all_sigs = list(calc_features(a, self.name, long=long))
            self.assertEqual(len(all_sigs), 1)
            sigs = all_sigs[0]
            rec = to_avro(sigs)
            for k in 'img_path', 'series', 'z', 'c', 't':
                rec[k] = getattr(self, k)
            try:
                pyavroc_emu.AvroSerializer(Signatures).serialize(rec)
            except AvroException as e:
                self.fail("Could not serialize record: %s" % e)
            self.assertEquals(rec["version"], sigs.feature_set_version)
            self.assertEquals(rec["name"], self.name)
            self.assertEquals((rec["x"], rec["y"]), (0, 0))
            self.assertEquals((rec["h"], rec["w"]), a.shape)
            fmap = dict(izip(sigs.feature_names, sigs.values))
            for fname, (vname, idx) in FEATURE_NAMES.iteritems():
                v = fmap.get(fname)
                if v is None:
                    assert not long
                    self.assertEqual(len(rec[vname]), 0)
                else:
                    self.assertEqual(rec[vname][idx], v)

    def test_tiling(self):
        a = make_random_data()
        w, h = 3, 4
        s = list(calc_features(a, self.name, w=w, h=h))
        self.assertEqual(len(s), 6)
        r = [to_avro(_) for _ in s]
        for i in xrange(6):
            for k in 'img_path', 'series', 'z', 'c', 't':
                r[i][k] = getattr(self, k)
        try:
            [pyavroc_emu.AvroSerializer(Signatures).serialize(_) for _ in r]
        except AvroException as e:
            self.fail("Could not serialize record: %s" % e)
        for i in xrange(6):
            self.assertEquals(r[i]["version"], s[i].feature_set_version)
            self.assertEquals(r[i]["name"], self.name)
            fmap = dict(izip(s[i].feature_names, s[i].values))
            for fname, (vname, idx) in FEATURE_NAMES.iteritems():
                v = fmap.get(fname)
                if v is None:
                    self.assertEqual(len(r[i][vname]), 0)
                else:
                    self.assertEqual(r[i][vname][idx], v)
        self.assertEqual(
            (r[0]["x"], r[0]["y"], r[0]["w"], r[0]["h"]), (0, 0, 3, 4))
        self.assertEqual(
            (r[1]["x"], r[1]["y"], r[1]["w"], r[1]["h"]), (3, 0, 3, 4))
        self.assertEqual(
            (r[2]["x"], r[2]["y"], r[2]["w"], r[2]["h"]), (6, 0, 2, 4))
        self.assertEqual(
            (r[3]["x"], r[3]["y"], r[3]["w"], r[3]["h"]), (0, 4, 3, 2))
        self.assertEqual(
            (r[4]["x"], r[4]["y"], r[4]["w"], r[4]["h"]), (3, 4, 3, 2))
        self.assertEqual(
            (r[5]["x"], r[5]["y"], r[5]["w"], r[5]["h"]), (6, 4, 2, 2))


def load_tests(loader, tests, pattern):
    test_cases = (TestGenTiles, TestFeatureCalc, TestToAvro)
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
