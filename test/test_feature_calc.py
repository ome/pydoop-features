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


SHAPE = (8, 8)
DTYPE = np.uint8


def make_random_data(filename=None):
    info = np.iinfo(DTYPE)
    a = np.random.randint(
        info.min, info.max, SHAPE[0] * SHAPE[1]
    ).astype(DTYPE).reshape(SHAPE)
    if filename is not None:
        with closing(TIFF.open(filename, mode="w")) as fo:
            fo.write_image(a)
    return a


class TestFeatureCalc(unittest.TestCase):

    def setUp(self):
        self.wd = tempfile.mkdtemp(prefix="pyfeatures_")
        self.fn = os.path.join(self.wd, "img.tiff")
        self.a = make_random_data(filename=self.fn)
        self.plane_tag = "img_0-z0000-c0000-t0000"

    def tearDown(self):
        shutil.rmtree(self.wd)

    def runTest(self):
        for long in False, True:
            sigs = calc_features(self.a, self.plane_tag, long=long)
            exp_sigs = FeatureVector(
                source_filepath=self.fn, long=long
            ).GenerateFeatures(write_to_disk=False)
            for name in "feature_names", "values", "feature_set_version":
                self.assertEquals(getattr(sigs, name), getattr(exp_sigs, name))


class TestToAvro(unittest.TestCase):

    def setUp(self):
        self.a = make_random_data()
        self.plane_tag = "img_0-z0000-c0000-t0000"

    def runTest(self):
        for long in False, True:
            sigs = calc_features(self.a, self.plane_tag, long=long)
            rec = to_avro(sigs)
            rec["plane_tag"] = self.plane_tag
            try:
                pyavroc_emu.AvroSerializer(Signatures).serialize(rec)
            except AvroException as e:
                self.fail("Could not serialize record: %s" % e)
            self.assertEquals(rec["version"], sigs.feature_set_version)
            fmap = dict(izip(sigs.feature_names, sigs.values))
            for fname, (vname, idx) in FEATURE_NAMES.iteritems():
                v = fmap.get(fname)
                if v is None:
                    assert not long
                    self.assertEqual(len(rec[vname]), 0)
                else:
                    self.assertEqual(rec[vname][idx], v)


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
