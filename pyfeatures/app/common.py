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

import logging

LOG_LEVELS = frozenset([
    "CRITICAL",
    "DEBUG",
    "ERROR",
    "FATAL",
    "INFO",
    "NOTSET",
    "WARN",
    "WARNING",
])
LOG_FORMAT = "%(asctime)s %(levelname)s: [%(name)s] %(message)s"


def get_log_level(s):
    try:
        return int(s)
    except ValueError:
        level_name = s.upper()
        if level_name in LOG_LEVELS:
            return getattr(logging, level_name)
        else:
            raise ValueError("%r is not a valid log level" % (s,))


def get_logger(name, level="INFO", f=None, mode="a"):
    logger = logging.getLogger(name)
    logger.setLevel(get_log_level(level))
    if isinstance(f, basestring):
        handler = logging.FileHandler(f, mode=mode)
    else:
        handler = logging.StreamHandler(f)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    return logger


class _NullHandler(logging.Handler):
    def emit(self, record):
        pass


class NullLogger(logging.Logger):
    def __init__(self):
        logging.Logger.__init__(self, "null")
        self.propagate = 0
        self.handlers = [_NullHandler()]
