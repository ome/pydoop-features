from wndcharm.FeatureVector import FeatureVector
from wndcharm.PyImageMatrix import PyImageMatrix


def calc_features(img_arr, plane_tag):
    assert len(img_arr.shape) == 2
    pychrm_matrix = PyImageMatrix()
    pychrm_matrix.allocate(img_arr.shape[1], img_arr.shape[0])
    numpy_matrix = pychrm_matrix.as_ndarray()
    numpy_matrix[:] = img_arr
    signatures = FeatureVector(basename=plane_tag)
    signatures.original_px_plane = pychrm_matrix
    signatures.GenerateFeatures()
    return signatures


def to_avro(signatures):
    try:
        rec = {
            'feature_names': signatures.feature_names,
            'values': signatures.values
        }
    except AttributeError:
        raise RuntimeError('"feature_names" and "values" are required attrs')
    for k in ('name', 'feature_set_version', 'source_filepath',
              'auxiliary_feature_storage'):
        try:
            rec[k] = getattr(signatures, k)
        except AttributeError:
            pass
    return rec
