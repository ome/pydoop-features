# BEGIN_COPYRIGHT
#
# Copyright (C) 2014-2017 Open Microscopy Environment:
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

import anydbm
import cPickle
import os
import re
import shelve
import shutil
import tempfile
import unittest
import warnings
from contextlib import closing

import pyfeatures.pyavroc_emu as pyavroc_emu
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import pyfeatures.app.dump as dump
from pyfeatures.app.common import NullLogger

LOGGER = NullLogger()
SCHEMA = """{
  "type": "record",
  "name": "Foo",
  "namespace": "it.crs4.features",
  "fields" : [{"name": "s", "type": "string"}, {"name": "i", "type": "int"}]
}"""


class Args(object):

    def __init__(self, **kw):
        if "in_fn" not in kw:
            raise ValueError("arg 'in_fn' is required")
        for k in "in_fn", "num_records", "out_fn", "format":
            setattr(self, k, kw.get(k))


class Base(unittest.TestCase):

    def setUp(self):
        self.records = [
            {"s": "a", "i": 1},
            {"s": "b", "i": 2},
        ]
        self.wd = tempfile.mkdtemp(prefix="pyfeatures_")
        self.fn = os.path.join(self.wd, "foo.avro")
        with open(self.fn, "w") as f:
            writer = pyavroc_emu.AvroFileWriter(f, SCHEMA)
            for r in self.records:
                writer.write(r)
            writer.close()

    def tearDown(self):
        shutil.rmtree(self.wd)


class TestDb(Base):

    def setUp(self):
        super(TestDb, self).setUp()
        self.out_fn = os.path.join(self.wd, "foo.db")
        self.args = Args(in_fn=self.fn, out_fn=self.out_fn, format="db")

    def test_full(self):
        dump.run(LOGGER, self.args)
        self.assertTrue(os.path.isfile(self.out_fn))
        with closing(shelve.open(self.out_fn, flag="r")) as shelf:
            for i, r in enumerate(self.records):
                self.assertEqual(shelf[str(i)], r)

    def test_num_records(self):
        self.args.num_records = 1
        dump.run(LOGGER, self.args)
        self.assertTrue(os.path.isfile(self.out_fn))
        with closing(shelve.open(self.out_fn, flag="r")) as shelf:
            self.assertEqual(shelf["0"], self.records[0])
            self.assertFalse("1" in shelf)

    def test_overwrite(self):
        with open(self.out_fn, "w") as f:
            f.write("")
        try:
            dump.run(LOGGER, self.args)
        except anydbm.error as e:
            self.fail("db creation failed: %s" % e)


class TestPickle(Base):

    def setUp(self):
        super(TestPickle, self).setUp()
        self.out_fn = os.path.join(self.wd, "foo.pickle")
        self.args = Args(in_fn=self.fn, out_fn=self.out_fn, format="pickle")

    def test_full(self):
        self.__run_test(self.args, self.records)

    def test_num_records(self):
        self.args.num_records = 1
        self.__run_test(self.args, self.records[:1])

    def __run_test(self, args, exp_records):
        dump.run(LOGGER, args)
        self.assertTrue(os.path.isfile(self.out_fn))
        with open(self.out_fn) as f:
            records = cPickle.load(f)
            self.assertEqual(records, exp_records)


class TestTxt(Base):

    def setUp(self):
        super(TestTxt, self).setUp()
        self.out_fn = os.path.join(self.wd, "foo.txt")
        self.args = Args(in_fn=self.fn, out_fn=self.out_fn, format="txt")

    def test_full(self):
        self.__run_test(self.args, self.records)

    def test_num_records(self):
        self.args.num_records = 1
        self.__run_test(self.args, self.records[:1])

    def __run_test(self, args, exp_records):
        dump.run(LOGGER, args)
        self.assertTrue(os.path.isfile(self.out_fn))
        self.assertEqual(self.__get_records(), exp_records)

    def __get_records(self):
        with open(self.out_fn) as f:
            return [eval(_) for _ in re.findall(r"{[^}]+}", f.read())]


def load_tests(loader, tests, pattern):
    test_cases = (TestDb, TestPickle, TestTxt)
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
