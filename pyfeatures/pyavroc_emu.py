# BEGIN_COPYRIGHT
#
# Copyright (C) 2016-2017 Open Microscopy Environment:
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

from cStringIO import StringIO

from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter, BinaryDecoder, BinaryEncoder
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


class AvroDeserializer(object):

    def __init__(self, schema_str):
        schema = avro.schema.parse(schema_str)
        self.reader = DatumReader(schema)

    def deserialize(self, rec_bytes):
        return self.reader.read(BinaryDecoder(StringIO(rec_bytes)))


class AvroSerializer(object):

    def __init__(self, schema_str):
        schema = avro.schema.parse(schema_str)
        self.writer = DatumWriter(schema)

    def serialize(self, record):
        f = StringIO()
        encoder = BinaryEncoder(f)
        self.writer.write(record, encoder)
        return f.getvalue()
