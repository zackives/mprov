import os, sys
import json
from mprov.metadata.stream_metadata import BasicSchema


class SourceDescriptor:
    schema = None

    def __init__(self, source_name: str, fields: list, types: list, metadata, identifier: object, frequency, files: list):
        self.source_name = source_name
        self.fields = fields
        self.types = types
        self.metadata = metadata
        self.identifier = identifier
        self.frequency = frequency
        self.files = files
        return

    def get_frequency(self):
        return self.frequency

    def get_name(self):
        return self.source_name

    def set_name(self, name: str):
        self.source_name = name

    def get_fields(self):
        return self.fields

    def get_types(self):
        return self.types

    def get_files(self):
        return self.files

    def get_file(self, index):
        return self.files[index]

    def get_source_id(self):
        return self.identifier

    def get_schema(self):
        if self.schema is not None:
            return self.schema

        types = []
        for i, f in enumerate(self.fields):
            types.append(self.types[i])
        names = self.fields.copy()
        names.insert(0, 'rid')
        types.insert(0, 'int')
        names.insert(1, 'timestamp')
        types.insert(1, 'int')
        names.insert(2, 'offset')
        types.insert(2, 'int')
        self.schema = BasicSchema(self.source_name, names, types)
        return self.schema


###
# Goes through CCortex directory tree and reconstructs sensor
# streams
class RegisterStreams:
    def sort_sensors(path) -> dict:
        ret = {}
        for entry in os.listdir(path):
            subject = path + '/' + entry
            if os.path.isdir(subject):
                print ("-- Subject -- ", subject)
                for date in os.listdir(subject):
                    date_path = subject + '/' + date
                    if os.path.isdir(date_path):
                        for sensor in os.listdir(date_path):
                            sensor_path = date_path + '/' + sensor
                            if os.path.isdir(sensor_path):
                                print ("** SENSOR", sensor, "**")
                                jsons = [file for file in os.listdir(sensor_path) if file.endswith('.json')]
                                gzips = [file for file in os.listdir(sensor_path) if file.endswith('.gz')]

                                jsons = [sensor_path + '/' + file for file in jsons]
                                gzips = [sensor_path + '/' + file for file in gzips]

                                print(jsons)
                                print(gzips)

                                json_file = jsons[0]
                                root = json.load(open(json_file))
                                schema = root['data_descriptor']
                                metadata = root['execution_context']
                                identifier = root['identifier']
                                name = root['name']

                                print (name, schema)

                                names = []
                                types = []
                                frequency = -1
                                if schema:
                                    for field in schema:
                                        names.append(field['NAME'])
                                        types.append(field['DATA_TYPE'])
                                        if 'FREQUENCY' in field:
                                            freq = field['FREQUENCY']
                                            if frequency == -1 or frequency > freq:
                                                frequency = freq

                                ret[name] = SourceDescriptor(name, names, types, metadata, identifier, frequency, gzips)
        return ret
