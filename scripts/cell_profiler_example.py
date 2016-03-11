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
Minimal distributed CP example.
"""

import logging
import logging.config
logging.root.setLevel(logging.INFO)
if len(logging.root.handlers) == 0:
    logging.root.addHandler(logging.StreamHandler())

import os
import uuid
import csv

import matplotlib
matplotlib.use('Agg')

import Image
import cellprofiler.preferences as cpprefs
cpprefs.set_headless()  # ASAP
cpprefs.set_allow_schema_write(False)
from cellprofiler.pipeline import Pipeline
from cellprofiler.utilities.cpjvm import cp_start_vm, cp_stop_vm

import pydoop.mapreduce.api as api
import pydoop.mapreduce.pipes as pp
from pydoop.avrolib import AvroContext

from pyfeatures.bioimg import BioImgPlane

# basename of the pipeline file, to be uploaded via distributed cache
PIPELINE_BN = 'it.crs4.features.cppipe'

# --- FIXME: the following info should be extracted from the pipeline file
CHANNEL_TAGS = ['D.TIF', 'F.TIF', 'R.TIF']
SET_SIZE = len(CHANNEL_TAGS)
RESULTS_BASENAMES = {
    'IMAGE': 'Image.csv',
    'NUCLEI': 'Nuclei.csv',
    'CELLS': 'Cells.csv',
    'CYTOPLASM': 'Cytoplasm.csv',
}
# -------------------------------------------------------------------------


class Mapper(api.Mapper):

    def __init__(self, ctx):
        super(Mapper, self).__init__(ctx)
        self.img_set = []
        self.cwd = os.getcwd()
        self.pipeline_filename = ctx.job_conf.get(PIPELINE_BN)
        cp_start_vm()
        self.ctx = ctx

    def map(self, ctx):
        p = BioImgPlane(ctx.value)
        if len(self.img_set) >= SET_SIZE:
            self.__process_current_set(ctx)
            self.img_set = []
        self.img_set.append(p)

    def __process_current_set(self, ctx):
        img_list = []
        for p, tag in zip(self.img_set, CHANNEL_TAGS):
            pixels = p.get_xy()
            im = Image.fromarray(pixels)
            out_fn = 'z%04d_%s' % (p.z, tag)
            im.save(out_fn)
            img_list.append(os.path.join(self.cwd, out_fn))
        results = self.__run_cp(img_list)
        ctx.emit(str(p.z), repr(results))

    def __run_cp(self, img_list):
        image_set_file = os.path.join(os.getcwd(), uuid.uuid4().hex)
        with open(image_set_file, 'w') as fo:
            for img in img_list:
                fo.write('%s\n' % img)
        cpprefs.set_image_set_file(image_set_file)
        out_dir = os.path.join(os.getcwd(), uuid.uuid4().hex)
        os.mkdir(out_dir)
        cpprefs.set_default_output_directory(out_dir)
        pipeline = Pipeline()
        pipeline.load(self.pipeline_filename)
        pipeline.read_file_list(image_set_file)
        pipeline.run(
            image_set_start=None,
            image_set_end=None,
            grouping=None,
            measurements_filename=None,
            initial_measurements=None
        )
        return self.__build_results_dict(out_dir)

    def __build_results_dict(self, out_dir):
        with open(os.path.join(out_dir, RESULTS_BASENAMES['IMAGE'])) as f:
            results = csv.DictReader(f).next()
        for tag in 'NUCLEI', 'CELLS', 'CYTOPLASM':
            with open(os.path.join(out_dir, RESULTS_BASENAMES[tag])) as f:
                results[tag] = list(csv.DictReader(f))
        return results

    def close(self):
        self.__process_current_set(self.ctx)
        cp_stop_vm()


def __main__():
    pp.run_task(pp.Factory(mapper_class=Mapper), context_class=AvroContext)
