'''
 Copyright 2020 Trustees of the University of Pennsylvania

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
import os
import logging
from pennprov.connection.mprov_connection import MProvConnection
from urllib3.exceptions import NewConnectionError


class MProvConnectionCache:
    class Key:
        def __init__(self, graph=None, user=None, password=None, host=None):
            self.graph = graph or MProvConnection.graph_name
            self.user = user or os.environ.get('MPROV_USER')
            self.password = password or os.environ.get('MPROV_PASSWORD')
            self.host = host or os.environ.get(
                'MPROV_HOST', MProvConnection.default_host)
            if not self.user:
                raise ValueError(
                    'either supply user or set environment variable MPROV_USER')
            if not self.password:
                raise ValueError(
                    'either supply password or set environment variable MPROV_PASSWORD')

        def __hash__(self):
            return hash((self.graph, self.user, self.password, self.host))

        def __eq__(self, other):
            return (self.graph, self.user, self.password, self.host) == (other.graph, other.user, other.password, other.host)

        def __ne__(self, other):
            return not self.__eq__(other)

    connections = {}

    @classmethod
    def get_connection(cls, connection_key):
         # type: (MProvConnectionCache.Key) -> MProvConnection
        connection = cls.connections.get(connection_key, None)
        if connection:
            logging.debug(
                'MProvConnectionCache: process %s retrieved cached connection %s', os.getpid(), id(connection))
        else:
            try:
                connection = MProvConnection(
                    connection_key.user, connection_key.password, connection_key.host)
                logging.debug(
                    'MProvConnectionCache: process %s created new connection %s', os.getpid(), id(connection))
            except Exception as e:
                logging.debug(e, exc_info=True)
                connection = None

            if connection:
                connection.set_graph(connection_key.graph)
                cls.connections[connection_key] = connection
        return connection
