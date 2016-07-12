pydoop-features OMERO scripts
=============================

These scripts can be used to link the output files from pydoop-features to OMERO.
You will need the `omero` Python module in your path.
In addition `omerofeatures.py` requires `omero.tables`, which requires Pytables.

- `map_series.py`: Create a TSV file containing OMERO object IDs
- `omerofeatures.py`: Convert avro files into an OMERO.features file.
- `concatfeatures.py`: Concatenate multiple OMERO.features files
