from __future__ import print_function

from typing import List, Any, Dict, Tuple, Mapping, Callable, Set
import logging

import uuid
from uuid import UUID

from pennprov.connection.provenance_store import ProvenanceStore

from psycopg2.extensions import cursor

class EventManager:
    # Unique UUID space for this thread / context
    uuid = None
    binding = 0

    store = None            # type: ProvenanceStore

    # ID to EVENT SET
    event_sets = {}         # type: Mapping[UUID, Set(Tuple)]
    # EVENT SET to ID
    inverse_events = {}     # type: Mapping[frozenset(Tuple), UUID]

    # Every node was created according to some event ID (which might also lead to many other things)
    # TODO: get rid of this?
    graph_to_events = {}

    def __init__(self,prov_store):
        # type: (ProvenanceStore) -> None
        self.store = prov_store
        #self.uuid = uuid.uuid4().int
        pass

    def _get_uuid(self):
        # type: () -> UUID
        #self.uuid = UUID(self.uuid + 1)
        return self.store.get_id()

    def get_event_expression_from_id(self, db, resource, result, id):
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
            self.get_event_expression_from_id(db, resource, result, event[5])
            self.get_event_expression_from_id(db, resource, result, event[6])
        else:
            logging.debug("Found event %s" %event)
            result.add(event)

        return result

    def create_base_event(self, db, resource, tuple):
        # type: (cursor, str, Tuple[Any]) -> str
        return self.extend_event_set(db, resource, tuple, None)[0]

    def extend_event_set(self, db, resource, tuple, existing_event):
        # type: (str, str, Tuple[Any], UUID) -> Tuple[str,bool]
        """
        Copy an event set node and add more items. This is done via composite events.
        """

        # A singleton set with the event tuple
        result = {tuple,}

        # Look up any items from the prior set (look up by its ID) and add
        # them to our set in the lattice
        if existing_event:
            result = self.get_event_expression_from_id(db, resource, result, \
                existing_event)
            
        # Are we adding a node event, or a node property event?
        uuid = None         # type: UUID
        nuuid = None        # type: UUID
        if tuple[0] == 'N':
            uuid = self.store.add_node_event(db, resource, tuple[1], '')
            logging.debug("Creating base node event: %s" %(str(uuid)))
        else:
            uuid = self.store.add_node_property_event(db, resource, tuple[1], tuple[2])
            logging.debug("Creating base property event: %s" %(str(uuid)))

        result = frozenset(result)
        if result not in self.inverse_events:
            nuuid = self._get_uuid()
            if existing_event:
                existing_event_uuid = self.event_sets[existing_event]
                uuid = self.store.add_compound_event(db, resource, existing_event_uuid, uuid)
                #logging.debug("Creating compound event: %s" %(str(uuid)))
                logging.debug("Extended (node-property) event: (e.%s/%s:%s)"%(nuuid,uuid,str(set(result))))
            else:
                logging.debug("Node event: (e.%s/%s:%s)"%(nuuid,uuid,str(set(result))))

            self.inverse_events[result] = nuuid
            self.event_sets[nuuid] = uuid#result

            # Temporary
            self.store.flush(db, resource)
            return (nuuid,True)
        else:
            # Reuse
            logging.debug("Node event %s reused: %s" %(self.inverse_events[result],str(set(result))))
            return (self.inverse_events[result],False)

    def extend_event_set_edge(self, db, resource, tuple, existing_event):
        # type: (str, str, Tuple[Any], UUID) -> Tuple[str,bool]
        """
        Copy an event set node and add more items
        """

        if existing_event:
            result = set()
            result = self.get_event_expression_from_id(db, resource, result, \
                existing_event)
            result = result.union(set([tuple]))
                #self.find_event_set(db, resource, existing_set))#self.event_sets[existing_set])
            
            result = frozenset(result)
        else:
            result = frozenset([tuple])

        uuid = self.store.add_edge_event(db, resource, tuple[1], tuple[2])

        if result not in self.inverse_events:
            nuuid = self._get_uuid()
            logging.debug("Edge create event: (%s,%s:%s)"%(nuuid,uuid,str(set(result))))
            self.inverse_events[result] = uuid
            self.event_sets[nuuid] = result
            return (nuuid,True)
        else:
            return (self.inverse_events[result],True)

    def _get_id(self):
        # type: () -> UUID
        return uuid.uuid4()

    def _get_id_from_key(self, key):
        # type: (str) -> UUID
        return uuid.uuid5(uuid.NAMESPACE_URL, key)


    def merge_subgraph_events(self, db, resource, node_list, event_op):
        # TODO: store this in the memo table
        logging.debug('--> New composite event to connect subgraphs: %s'%str(event_op))
        event_1 = event_op[1] # type: UUID
        event_2 = event_op[2]
        edge = event_op[3]
        id = self._get_id_from_key(resource + ':' + str(event_1) + '.' + str(edge) + '.' + str(event_2) + "\\D")# + str(args))

        # Add the appropriate event to the queue
        self.store.event_queue.append((id, resource, event_op[0], edge, None, str(event_1), str(event_2)))#args))

        #self.graph_to_events[tuple(node_list)] = id

        self.event_sets[id] = id
        # TODO:
        #self.inverse_events[result] = nuuid

        # TODO: remove
        #self.flush(db, resource)
        #self._write_dirty_nodes(db, resource)
        self.store.flush(db, resource)

        return

