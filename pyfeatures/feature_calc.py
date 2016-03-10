from itertools import izip

from wndcharm.FeatureVector import FeatureVector
from wndcharm.PyImageMatrix import PyImageMatrix

from pyfeatures.feature_names import FEATURE_NAMES


def get_image_matrix(img_array):
    if len(img_array.shape) != 2:
        raise ValueError("array must be two-dimensional")
    image_matrix = PyImageMatrix()
    image_matrix.allocate(img_array.shape[1], img_array.shape[0])
    numpy_matrix = image_matrix.as_ndarray()
    numpy_matrix[:] = img_array
    return image_matrix


def calc_features(img_array, plane_tag, long=False):
    signatures = FeatureVector(basename=plane_tag, long=long)
    signatures.original_px_plane = get_image_matrix(img_array)
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
