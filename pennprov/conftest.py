'''
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
'''
from pennprov.connection.mprov_connection_cache import MProvConnectionCache
import pytest
from pennprov.connection.mprov import MProvConnection

@pytest.fixture
def mprov_conn():
    mprov_conn = MProvConnection()
    if not mprov_conn:
        raise RuntimeError('Could not connect')
    mprov_conn.create_or_reset_graph()
    yield mprov_conn
    mprov_conn.close()


@pytest.fixture
def cached_mprov_conn():
    connection_key = MProvConnectionCache.Key()
    mprov_conn = MProvConnectionCache.get_connection(connection_key)
    if not mprov_conn:
        raise RuntimeError('Could not connect')
    mprov_conn.create_or_reset_graph()
    yield mprov_conn
    MProvConnectionCache.expire(connection_key)

