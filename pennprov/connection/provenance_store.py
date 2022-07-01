import os
from pennprov.config import config

import logging

from typing import List, Any, Dict, Tuple, Mapping, Callable, Set

import uuid
from uuid import UUID

class Factory:
    registered_index_types = dict() # type: Mapping[str, Callable[[], ProvenanceStore]]

    @classmethod 
    def register_index_type(cls, key, creator):
        # type: (str, Callable[[], ProvenanceStore]) -> None 
        cls.registered_index_types[key.lower()] = creator

    @classmethod
    def get_index(cls):
        # type: () -> ProvenanceStore
        """
        Retrieve the appropriate provenance indexing subsystem
        """
        key = os.environ.get('MPROV_INDEX')
        if key is None:
            key = config.provenance.get('index', 'new')

        creator = cls.registered_index_types.get(key.lower())

        if creator is None:
            raise ValueError(f'no creator registered for {key}')
        return creator()


class ProvenanceStore:
    """
    A persistent provenance graph storage subsystem.
    """

    Factory.register_index_type('no-op', lambda: ProvenanceStore())

    def add_node(self, db, resource, label, skolem_args):
        # type: (cursor, str, str, List[Any]) -> None
        logging.info('Node ' + str(label) + str(skolem_args))
        return 1

    def add_edge(self, db, resource, source, label, dest):
        # type: (cursor, str, str, str, str) -> None
        logging.info('Edge ' + str(source) + str(label) + str(dest))
        return 1

    def add_nodeprop(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, Any, int) -> None
        return 1

    def flush(self, db, resource):
        logging.info('Flush')
        return

    def reset(self):
        logging.info('Reset')
        return

    def create_tables(self, cursor):
        # type: (cursor) -> None
        return

    def clear_tables(self, db, graph):
        # type: (cursor, str) -> None
        return

    def get_provenance_data(self, db, resource, token):
        # type: (cursor, str, str) -> List[Dict]
        return

    def get_connected_to(self, db, resource, token, label1):
        # type: (cursor, str, str, str) -> List[str]
        return

    def get_connected_from(self, db, resource, token, label1):
        # type: (cursor, str, str, str) -> List[str]
        return

    def get_connected_to_labeled(self, db, resource, token, label1):
        # type: (cursor, str, str, str) -> List[Tuple(str,str)]
        return

    def get_connected_from_labeled(self, db, resource, token, label1):
        # type: (cursor, str, str, str) -> List[Tuple(str,str)]
        return

    def get_edges(self, db, resource):
        #type: (cursor, str) -> List[Tuple]
        return []

    def get_nodes(self, db, resource):
        #type: (cursor, str) -> List[Dict]
        return []

    def get_id(self):
        # type: () -> UUID
        return uuid.uuid4()

    def get_id_from_key(self, key):
        # type: (str) -> UUID
        return uuid.uuid5(uuid.NAMESPACE_URL, key)

