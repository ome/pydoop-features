from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter
import avro.schema


class AvroFileReader(DataFileReader):

    def __init__(self, f, types=False):
        if types:
            raise RuntimeError('types not supported')
        super(AvroFileReader, self).__init__(f, DatumReader())


class AvroFileWriter(DataFileWriter):

    def __init__(self, f, schema_json):
        schema = avro.schema.parse(schema_json)
        super(AvroFileWriter, self).__init__(f, DatumWriter(), schema)

    def write(self, datum):
        return super(AvroFileWriter, self).append(datum)
