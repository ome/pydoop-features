"""\
Integrate bioimage analysis with Bio-Formats and Hadoop.
"""

from distutils.core import setup


NAME = "pyfeatures"
DESCRIPTION = __doc__
URL = "https://github.com/simleo/pydoop-features.git"
CLASSIFIERS = [
    "Programming Language :: Python",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
    "Intended Audience :: Science/Research",
]


setup(
    name=NAME,
    description=DESCRIPTION,
    url=URL,
    classifiers=CLASSIFIERS,
    packages=["pyfeatures"],
)
