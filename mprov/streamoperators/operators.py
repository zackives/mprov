from mprov.metadata.stream_metadata import BasicSchema, BasicTuple
from mprov.connection.mprov_connection import MProvConnection
from typing import List


class Source(object):
    """ Basic stream source """
    def initialize(self):
        return

    # Return any tuple(s) available for processing,
    # or None for end of stream
    def poll(self, max: int):
        return []

    def close(self):
        return

    def get_name(self):
        return 'Source'


class Sink(object):
    """
    A stream sink, i.e., consumer of tuples
    """
    def initialize(self, stream_schemas: List[BasicSchema]):
        return

    # Process a tuple from a given source stream
    # (the source_name may be useful if this is an n-ary operator)
    def process(self, source_name: str, tuple):
        return

    def close(self):
        return


class StreamOperator(Source, Sink):
    """
    An operator, akin to a Bolt in Storm,
    should be both source and sink
    """
    input_schemas = []
    output_schema = {}
    outputs = []
    prov_connection = None
    name = ''
    done = False

    def __init__(self, name: str, prov_connection: MProvConnection):
        self.name = name
        self.connection = prov_connection
        return

    def initialize(self):
        return

    def initialize(self, stream_schemas: List[BasicSchema]):
        self.input_schemas = stream_schemas
        self.initialize()
        return

    def process(self, source: str, input_tuple: BasicTuple):
        return

    # Return any tuple(s) available for processing,
    # from the internal queue, or None if done = true
    # and we have nothing in the queue
    def poll(self, max_count: int):
        ret = []
        for i in range(0,max_count):
            if len(self.outputs) > 0:
                if self.outputs[0]:
                    ret.append(self.outputs[0])
                del self.outputs[0]

        if len(ret) >= 0 or not self.done:
            return ret
        else:
            return None

    def close(self):
        return

    def get_name(self):
        return self.name


class StreamSource(Source):
    """
    An operator that is just a source of tuples,
    akin to a Spout in Apache Storm
    """
    output_schema = {}
    output_schema_name = ''
    outputs = []
    prov_connection = None
    name = ''
    done = False

    def __init__(self, name: str, prov_connection: MProvConnection):
        self.name = name
        self.output_schema_name = name
        self.connection = prov_connection
        return

    def initialize(self):
        return

    def get_name(self):
        return self.name
