import pytest
import logging

import pennprov.connection.mprov as mprov

class TestMProv:
    conn = None

    def test_create(self):
        self.conn = mprov.MProvConnection()
        assert self.conn is not None

        self.conn.create_or_reset_graph()
        self.conn.create_or_reuse_graph()

        self.conn.store_stream_tuple('first_stream', 0, {'start': 1, 'end': 2})
        self.conn.store_annotation('first_stream', 0, 'ann1', 30)

        self.conn.store_activity('area_circle', 0, 1, 0)
        self.conn.store_code('import pytest\nimport logging\n')



