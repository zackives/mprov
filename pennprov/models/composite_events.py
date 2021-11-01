from __future__ import print_function

from typing import List, Any, Dict, Tuple, Mapping, Callable, Set
import logging

import uuid
from uuid import UUID

#from pennprov.connection.dblayer import EventBindingProvenanceStore

from psycopg2.extensions import cursor

class EventManager:
    # Unique UUID space for this thread / context
    uuid = None
    binding = 0

    store = None            # type: EventBindingProvenanceStore

    # ID to EVENT SET
    event_sets = {}         # type: Mapping[UUID, Set(Tuple)]
    # EVENT SET to ID
    inverse_events = {}     # type: Mapping[Set(Tuple), UUID]

    # Every node was created according to some event ID (which might also lead to many other things)
    # TODO: get rid of this?
    graph_to_events = {}

    def __init__(self,prov_store):
        # type: (EventBindingProvenanceStore) -> None
        self.store = prov_store
        self.uuid = uuid.uuid4().int
        pass

    def _get_uuid(self):
        # type: () -> UUID
        self.uuid = self.uuid + 1
        return self.uuid -1

    def get_event_set_from_id(self, db, resource, result, id):
        #result = set.union(result, self.event_sets[id])
        """
        Given an eventset UUID, find all associated events.  May require transitive closure
        if there are composite events.  The "C" and "D" composite events reference child events,
        leading to the recursive case.
        """

        event = self.store.get_event(db, resource, id)

        # An event with children, find recursively
        if event == None:
            return result
        if event[2] == 'C' or event[2] == 'D':
            self.get_event_set_from_id(db, resource, result, event[5])
            self.get_event_set_from_id(db, resource, result, event[6])
        else:
            result.add(event)

        return result

    def extend_event_set_from_base(self, db, resource, tuple, baseline):
        # type: (str, str, Tuple[Any], str) -> Tuple[str,bool]
        return self.extend_event_set(db, resource, tuple,\
            self.find_event_set(db, resource, baseline))

    def extend_event_set(self, db, resource, tuple, existing_set):
        # type: (str, str, Tuple[Any], str) -> Tuple[str,bool]
        """
        Copy an event set node and add more items. This is done via composite events.
        """

        # A singleton set with the event tuple
        result = set([tuple])

        # Look up any items from the prior set (look up by its ID) and add
        # them to our set in the lattice
        if existing_set:
            result = self.get_event_set_from_id(db, resource, result, self.find_event_set(db, resource, existing_set))#self.event_sets[existing_set])
            
        result = frozenset(result)

        # Are we adding a node event, or a node property event?
        if tuple[0] == 'N':
            uuid = self.store.add_node_event(db, resource, tuple[1], '')
        else:
            uuid = self.store.add_node_property_event(db, resource, tuple[1], tuple[2])

        if existing_set:
            uuid = self.store.add_compound_event(db, resource, self.event_sets[existing_set], uuid)

        if result not in self.inverse_events:
            nuuid = self._get_uuid()
            logging.debug("Node event: (%s,%s:%s)"%(nuuid,uuid,str(result)))

            self.inverse_events[result] = nuuid
            self.event_sets[nuuid] = uuid#result
            return (nuuid,True)
        else:
            # Reuse
            return (self.inverse_events[result],False)

    def extend_event_set_edge(self, db, resource, tuple, existing_set):
        # type: (str, str, Tuple[Any], str) -> Tuple[str,bool]
        """
        Copy an event set node and add more items
        """

        if existing_set:
            result = set([tuple]).union(self._find_event_set(db, resource, existing_set))#self.event_sets[existing_set])
            
            result = frozenset(result)
        else:
            result = frozenset([tuple])

        uuid = self.store.add_edge_event(db, resource, tuple[1], tuple[2])

        if result not in self.inverse_events:
            nuuid = self._get_uuid()
            logging.debug("Edge event: (%s,%s:%s)"%(nuuid,uuid,str(result)))
            self.inverse_events[result] = uuid
            self.event_sets[nuuid] = result
            return (nuuid,True)
        else:
            return (self.inverse_events[result],True)


    def find_event_set(self, db, resource, id):
        # type: (cursor, str, Tuple) -> Set[Any]
        if id in self.graph_to_events:
            return self.graph_to_events[id]
        else:
            return None

    def associate_event(self, tup, id):
        # type: (Tuple[Any], UUID) -> None
        self.graph_to_events[tup] = id

    def merge_subgraph_events(self, db, resource, node_list, event_op):
        # TODO: store this in the memo table
        logging.debug('--> New composite event to connect subgraphs: %s'%str(event_op))
        event_1 = event_op[1] # type: UUID
        event_2 = event_op[2]
        edge = event_op[3]
        id = self._get_id_from_key(resource + ':' + str(event_1) + '.' + str(edge) + '.' + str(event_2) + "\\D")# + str(args))

        self.store.event_queue.append((id, resource, event_op[0], edge, None, str(event_1), str(event_2)))#args))

        self.graph_to_events[tuple(node_list)] = id

        self.event_sets[id] = id
        # TODO:
        #self.inverse_events[result] = nuuid

        # TODO: remove
        #self.flush(db, resource)
        #self._write_dirty_nodes(db, resource)
        self.store.flush(db, resource)

        return

