from itertools import izip

from wndcharm.FeatureVector import FeatureVector
from wndcharm.PyImageMatrix import PyImageMatrix

from pyfeatures.feature_names import FEATURE_NAMES


def calc_features(img_arr, plane_tag, long=False):
    assert len(img_arr.shape) == 2
    pychrm_matrix = PyImageMatrix()
    pychrm_matrix.allocate(img_arr.shape[1], img_arr.shape[0])
    numpy_matrix = pychrm_matrix.as_ndarray()
    numpy_matrix[:] = img_arr
    signatures = FeatureVector(basename=plane_tag, long=long)
    signatures.original_px_plane = pychrm_matrix
    signatures.GenerateFeatures(write_to_disk=False)
    return signatures


def to_avro(signatures):
    rec = dict((_[0], []) for _ in FEATURE_NAMES.itervalues())
    for fname, value in izip(signatures.feature_names, signatures.values):
        vname, idx = FEATURE_NAMES[fname]
        rec[vname].append((idx, value))
    for vname, tuples in rec.iteritems():
        rec[vname] = [_[1] for _ in sorted(tuples)]
    rec["version"] = signatures.feature_set_version
    rec["plane_tag"] = signatures.basename
    return rec
