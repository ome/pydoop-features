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
import tempfile
import shutil
import os
from contextlib import closing
from itertools import izip

import numpy as np
from libtiff import TIFF
from avro.schema import AvroException
from wndcharm.FeatureVector import FeatureVector

from pyfeatures.feature_calc import calc_features, to_avro
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


class TestFeatureCalc(unittest.TestCase):

    def setUp(self):
        self.wd = tempfile.mkdtemp(prefix="pyfeatures_")
        self.plane_tag = "img_0-z0000-c0000-t0000"

    def tearDown(self):
        shutil.rmtree(self.wd)

    def test_no_tiling(self):
        a = make_random_data()
        for long in False, True:
            all_sigs = list(calc_features(a, self.plane_tag, long=long))
            self.assertEqual(len(all_sigs), 1)
            sigs = all_sigs[0]
            self.assertEqual((sigs.x, sigs.y, sigs.w, sigs.h), (0, 0, W, H))
            exp_sigs = self.__get_exp_features(a, long=long)
            self.assertFeaturesEqual(sigs, exp_sigs)

    def test_tiling(self):
        a = make_random_data()
        w, h = 3, 4
        s = list(calc_features(a, self.plane_tag, w=w, h=h))
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

    def assertFeaturesEqual(self, fv1, fv2):
        for name in "feature_names", "values", "feature_set_version":
            self.assertEquals(getattr(fv1, name), getattr(fv2, name))

    def __get_exp_features(self, a, long=False):
        fn = os.path.join(self.wd, "img.tiff")
        dump_to_tiff(a, fn)
        fv = FeatureVector(source_filepath=fn, long=long)
        return fv.GenerateFeatures(write_to_disk=False)


class TestToAvro(unittest.TestCase):

    def setUp(self):
        self.plane_tag = "img_0-z0000-c0000-t0000"

    def test_no_tiling(self):
        a = make_random_data()
        for long in False, True:
            all_sigs = list(calc_features(a, self.plane_tag, long=long))
            self.assertEqual(len(all_sigs), 1)
            sigs = all_sigs[0]
            rec = to_avro(sigs)
            try:
                pyavroc_emu.AvroSerializer(Signatures).serialize(rec)
            except AvroException as e:
                self.fail("Could not serialize record: %s" % e)
            self.assertEquals(rec["version"], sigs.feature_set_version)
            self.assertEquals(rec["plane_tag"], self.plane_tag)
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
        s = list(calc_features(a, self.plane_tag, w=w, h=h))
        self.assertEqual(len(s), 6)
        r = [to_avro(_) for _ in s]
        try:
            [pyavroc_emu.AvroSerializer(Signatures).serialize(_) for _ in r]
        except AvroException as e:
            self.fail("Could not serialize record: %s" % e)
        for i in xrange(6):
            self.assertEquals(r[i]["version"], s[i].feature_set_version)
            self.assertEquals(r[i]["plane_tag"], self.plane_tag)
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
    test_cases = (TestFeatureCalc, TestToAvro)
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
