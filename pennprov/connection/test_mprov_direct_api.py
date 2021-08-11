"""
 Copyright 2021 Trustees of the University of Pennsylvania
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

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



