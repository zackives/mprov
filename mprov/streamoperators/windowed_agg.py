from .operators import StreamOperator
from mprov.metadata.stream_metadata import BasicSchema, BasicTuple
from mprov.connection.mprov_connection import MProvConnection
import io, sys
from pennprov import ProvTokenModel, QualifiedName
from pennprov.rest import ApiException
from typing import List


class WindowedAggregateOp(StreamOperator):
    output_schema = None
    window_size = 0
    slide = 0
    agg_fn = None
    agg_field = ''
    window_ids = {}

    # Window structure: input name -> list of tuples in the window
    windows = {}

    def __init__(self, name: str, window_size: int, slide: int, agg_field: str, fn, connection: MProvConnection):
        super(WindowedAggregateOp, self).__init__(name, connection)
        self.window_size = window_size
        self.slide = slide
        self.agg_field = agg_field
        self.agg_fn = fn

        self.output_schema = BasicSchema(name)
        self.output_schema.add_field(agg_field + str(window_size), 1.)

    def initialize(self):
        return super.initialize()

    def process(self, source: str, input_tuple: BasicTuple):
        if source not in self.windows:
            self.windows[source] = []
            self.window_ids[source] = 0

        self.windows[source].append(input_tuple.data.copy())

        if len(self.windows[source]) == self.window_size:
            self.write_provenance(source, self.windows[source], self.window_ids[source])

            projection = [float(p[self.agg_field]) for p in self.windows[source]]

            agg_result = self.agg_fn(projection)

            for i in range(0, self.slide):
                del self.windows[source][0]

            ret_tuple = self.output_schema.create_tuple_list([agg_result])
            self.outputs.append(ret_tuple)

            self.window_ids[source] = self.window_ids[source] + 1

    def write_provenance(self, input_name: str, window: List[dict], window_id: int):
        """
        Write the tuple to the provenance store, along with our index position
        and stream name.

        If the tuple contains a location, we also write it as an annotation

        :param window: The window of data on the stream
        :return: None
        """
        window_ids = [self.connection.get_entity_id(input_name, int(t['rid'])) for t in window]
        self.connection.store_window_and_inputs(self.name, window_id, window_ids)

