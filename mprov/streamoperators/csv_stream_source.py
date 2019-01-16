from .operators import StreamSource
from mprov.connection.mprov_connection import MProvConnection
from mprov.metadata.stream_metadata import BasicSchema, BasicTuple
import io, sys
from pennprov import ProvTokenModel, QualifiedName
from pennprov.rest import ApiException
import gzip


class CsvStreamSource(StreamSource):
    count = 0
    cursor = 0
    field_names = []
    field_values = []
    reader = None
    schema = None

    def __init__(self, name: str, source_descriptor, field_names: list, field_values: list, connection: MProvConnection):
        super().__init__(name, connection)
        print('Initializing', name)
        self.source = source_descriptor
        self.output_schema_name = name
        source_descriptor.set_name(name)

        self.schema = self.source.get_schema()
        self.schema.add_field('streamid','string')
        self.schema.add_field('_prov','string')

        if field_names:
            for i, field in enumerate(field_names):
                self.schema.add_field(field, field_values[i])

        self.field_names = field_names
        self.field_values = field_values

    def initialize(self):
        print('Reading', self.source.get_name(), self.source.get_file(self.cursor))
        self.reader = gzip.GzipFile(self.source.get_file(self.cursor), mode="r")

    def delay_time(self):
        delay = self.source.frequency
        # TODO if we want: sleep for 1 / freq
        return

    def poll(self, max_count: int):
        self.delay_time()
        try:
            read = False
            line = self.reader.readline()

            read = len(line) > 0

            if read:
                line = line.rstrip().decode('utf-8')
                values = line.split(',')
                tup = self.schema.create_tuple()

                tup['rid'] = self.get_tuple_index()
                self.inc_tuple_index()
                tup['streamid'] = self.schema.get_name()
                for i, k in enumerate(self.schema.fields):
                    if i < len(self.schema.fields) - 3 and k != 'rid':
                        tup[k] = values[i - 1]

                for i, k in enumerate(self.field_names):
                    tup[k] = self.field_values[i]


                self.write_provenance(tup)

                return [tup]
            else:
                self.done = True
                self.reader.close()
                self.cursor = self.cursor + 1

                if self.cursor >= len(self.source.files):
                    return None
                else:
                    self.reader = gzip.GzipFile(self.source.get_file(self.cursor), mode="r")
                    return self.poll(max_count)
        except BaseException as e:
            print (e)
            return None

    def get_tuple_index(self):
        return self.count

    def inc_tuple_index(self):
        self.count = self.count + 1

    def write_provenance(self, tuple):
        """
        Write the tuple to the provenance store, along with our index position
        and stream name.

        If the tuple contains a location, we also write it as an annotation

        :param tuple: The data on the stream
        :return: None
        """
        self.connection.store_stream_tuple(self.name, self.get_tuple_index(), tuple)

        #if "Location Name" in tuple.schema.fields:
        if "Accelerometer X" in tuple.schema.fields:
            self.connection.store_annotation(self.name, self.get_tuple_index(),\
                                             'sensor', str(tuple['Accelerometer X']))
