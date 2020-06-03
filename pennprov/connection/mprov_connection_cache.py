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

logger = logging.getLogger(__name__)


class MProvConnectionCache:
    """
    A simple in-memory cache for MProvConnections
    where the connections are stored in a class variable dict.
    """
    class Key:
        """
        A key for the connection cache. Instances should not be modified after instantiation.
        """

        def __init__(self, graph=MProvConnection.graph_name, user=None, password=None, host=None):
            # type: (str, str, str, str) -> MProvConnectionCache.Key
            """
            :param graph:    The name of the graph with which this connection will be interacting.
                             Defaults to MProvConnection.graph_name
            :param user:     The username to use for the connection.
                             Defaults to the value of the environment variable MPROV_USER
            :param password: The password to use for the connection.
                             Defaults to the value of the environment variable MPROV_PASSWORD
            :param host:     The host to use for the connection, e.g., 'http://localhost:1234'
                             Defaults to the value of the environment variable MPROV_HOST if set,
                             otherwise to MProvConnection.default_host
            :raises:         ValueError if user is None and MPROV_USER is not set
                             or if password is None and MPROV_PASSWORD is not set
            """
            self.graph = graph
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
        """
        Returns a cached MProvConnection for the given key if one has been previously cached.
        Otherwise, attempts to create, cache, and return a newly created connection.
        If the connection cannot be created, None is returned and the error is logged at the DEBUG level.

        :param connection_key: an MProvConnectionCache.Key
        :return: the connection associated with connection_key or a newly created connection
        """
        connection = cls.connections.get(connection_key, None)
        if connection:
            logger.debug(
                'MProvConnectionCache: process %s retrieved cached connection %s', os.getpid(), id(connection))
        else:
            try:
                connection = MProvConnection(
                    connection_key.user, connection_key.password, connection_key.host)
                connection.set_graph(connection_key.graph)

                logger.debug(
                    'MProvConnectionCache: process %s created new connection %s', os.getpid(), id(connection))
            except Exception as e:
                logger.debug(e, exc_info=True)
                connection = None

            if connection:
                cls.connections[connection_key] = connection
        return connection
