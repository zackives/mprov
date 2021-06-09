import pytest
import logging

import pennprov.connection.mprov as mprov

class TestMProv:
    conn = None

    def test_create(self):
        self.conn = mprov.MProvConnection()
        assert self.conn is not None

    def test_init_graph(self):
        self.conn.create_or_reset_graph()
        self.conn.create_or_reuse_graph()



