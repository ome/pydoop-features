from wndcharm.FeatureVector import SlidingWindow
from wndcharm.FeatureSpace import FeatureSpace
from wndcharm.PyImageMatrix import PyImageMatrix

def calc_features(img_arr, plane_tag, long=False):
    assert len(img_arr.shape) == 2
    pychrm_matrix = PyImageMatrix()
    pychrm_matrix.allocate(img_arr.shape[1], img_arr.shape[0])
    numpy_matrix = pychrm_matrix.as_ndarray()
    numpy_matrix[:] = img_arr
    kwargs = {}
    kwargs['w'] = 200
    kwargs['h'] = 200
    kwargs['deltax'] = 200
    kwargs['deltay'] = 200
    kwargs['original_px_plane'] = numpy_matrix
    kwargs['basename'] = plane_tag
    window_iter = SlidingWindow( **kwargs )
    feature_space = FeatureSpace.NewFromSlidingWindow(window_iter, n_jobs=None, quiet=True)

    #signatures = FeatureVector(basename=plane_tag, long=long)
    #signatures.original_px_plane = pychrm_matrix
    #signatures.GenerateFeatures(write_to_disk=False)

    # Note, now the type of object returned isn't FeatureVector, but FeatureSpace
    return feature_space


def to_avro(feature_space):
    try:
        rec = {
            'feature_names': feature_space.feature_names,
            #'values': signatures.values
            # values:data_matrix::FeatureVector:FeatureSpace
            'data_matrix' : feature_space.data_matrix
        }
    except AttributeError:
        raise RuntimeError('"feature_names" and "data_matrix" are required attrs')
    for k in ('name', 'feature_set_version', 'source_filepath', ):
              #'auxiliary_feature_storage'):
        try:
            rec[k] = getattr(feature_space, k)
        except AttributeError:
            pass
    return rec
