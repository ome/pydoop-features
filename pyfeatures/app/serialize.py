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

"""\
Serialize image data to BioImgPlane records.

All args are passed to it.crs4.features.ImageToAvro.
"""

import subprocess as sp

from pyfeatures import JAR_PATH


def run(args, extra_argv=None):
    if extra_argv is None:
        extra_argv = []
    sp_argv = ["java", "-cp", JAR_PATH, "it.crs4.features.ImageToAvro"]
    sp_argv.extend(extra_argv)
    try:
        sp.check_call(sp_argv, stdout=args.stdout, stderr=args.stderr)
    except sp.CalledProcessError:
        if extra_argv:
            raise
    return 0


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "serialize",
        description=__doc__,
        epilog="Run without arguments to print the Java help."
    )
    parser.set_defaults(func=run)
    return parser
