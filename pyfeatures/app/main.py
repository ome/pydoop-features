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

"""\
Pyfeatures command line tool.
"""

import sys
import argparse
import importlib

from .common import get_log_level, get_logger


VERSION = "NOT_TAGGED_YET"
SUBMOD_NAMES = [
    "calc",
    "deserialize",
    "dump",
    "plot",
    "serialize",
    "tiles",
]


def log_level(s):
    try:
        return get_log_level(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(e.message)


def make_parser():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('-V', '--version', action='version', version=VERSION,
                        help='print version tag and exit')
    parser.add_argument('--log-level', metavar="LEVEL", type=log_level,
                        default="INFO", help="logging level")
    subparsers = parser.add_subparsers(help="sub-commands", dest="command")
    for n in SUBMOD_NAMES:
        mod = importlib.import_module("%s.%s" % (__package__, n))
        mod.add_parser(subparsers)
    return parser


def main(argv=None):
    parser = make_parser()
    args, extra_argv = parser.parse_known_args(argv)
    logger = get_logger(args.command, level=args.log_level, f=sys.stdout)
    logger.info("START")
    args.func(logger, args, extra_argv=extra_argv)
    logger.info("STOP")
