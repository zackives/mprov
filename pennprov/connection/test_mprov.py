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

    def test_create_or_reset(self):
        self.conn = mprov.MProvConnection()

        self.conn.create_or_reset_graph()
        self.conn.store_stream_tuple('first_stream', 0, {'start': 1, 'end': 2})
        self.conn.store_annotation('first_stream', 0, 'ann1', 30)

        self.conn.create_or_reset_graph()

        node_count = None
        node_prop_count = None
        edge_count = None
        edge_prop_count = None
        with self.conn.graph_conn as db_conn:
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM MProv_Node WHERE _resource = %s", (self.conn.get_graph(),))
                node_count = cursor.fetchall()
                cursor.execute("SELECT COUNT(*) FROM MProv_NodeProp WHERE _resource = %s", (self.conn.get_graph(),))
                node_prop_count = cursor.fetchall()
                cursor.execute("SELECT COUNT(*) FROM MProv_Edge WHERE _resource = %s", (self.conn.get_graph(),))
                edge_count = cursor.fetchall()
                cursor.execute("SELECT COUNT(*) FROM MProv_EdgeProp WHERE _resource = %s", (self.conn.get_graph(),))
                edge_prop_count = cursor.fetchall()

        # create_or_reset_graph should delete everything, but then create a new Agent node
        assert node_count == [(1,)]
        assert node_prop_count == [(1,)]
        assert edge_count == [(0,)]
        assert edge_prop_count == [(0,)]

        agent_node = self.conn.get_node(self.conn.get_username())
        assert agent_node is not None




