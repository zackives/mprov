from __future__ import print_function

from typing import List, Any, Dict, Tuple, Mapping, Callable, Set
import logging

from psycopg2.extensions import cursor

from pennprov.models.composite_events import EventManager
#from pennprov.connection.dblayer import EventBindingProvenanceStore

import uuid
from uuid import UUID

class Subgraph:
    """
    A subgraph
    """
    creation_event = None       # type: UUID
    event_manager = None        # type: EventManager
    node_set = frozenset()      # type: frozenset[UUID]

    node_mapping = []           # type: List[UUID]

    internal_edges = None       # type: Mapping[UUID,Tuple[str,UUID]]
    external_edges = None       # type: List[Tuple[UUID,str,UUID]]

    maximal = None              # type: Subgraph

    def __init__(self, initial_nodeset, emgr, creation_event):
        # type: (Set[UUID], EventBindingProvenanceStore, UUID) -> None
        self.node_set = frozenset(initial_nodeset)
        self.event_manager = emgr
        self.creation_event = creation_event
        self.internal_edges = {}
        self.external_edges = []
        self.maximal = self
        logging.debug("Creating new subgraph with event %s:(%s)"%(creation_event,str(initial_nodeset)))

    def merge(first, second, new_event):
        # type: (Subgraph,Subgraph,UUID) -> Subgraph
        """
        Merge two subgraphs, with the new_event has the main "bridge" event
        """
        ret = Subgraph(first.node_set.union(second.node_set), first.event_manager, new_event)
        ret.internal_edges = first.internal_edges.copy().update(second.internal_edges)
        ret.external_edges = first.external_edges + second.external_edges
        ret.node_mapping = first.node_mapping + second.node_mapping
        first.set_maximal(ret)
        second.set_maximal(ret)
        ret.reclassify_internal_edges()
        return ret

    def add_event(self, new_event):
        # type: (UUID) -> Subgraph
        """
        Merge two subgraphs, with the new_event has the main "bridge" event
        """
        self.creation_event = new_event
        return self

    def add_external_edges(self, db, resource, node_id):
        # type: (cursor, str, str) -> None
        """
        Given a new frontier node, find any adjacent edges and add them
        to our external-facing set
        """
        for (src,label) in self.store.get_connected_from_label(db, resource, node_id, None):
            self.external_edges.append((src,label,node_id))

        for (dest,label) in self.store.get_connected_to_label(db, resource, node_id, None):
            self.external_edges.append((node_id,label,dest))
        return

    def get_graph_connected(self,node):
        # type: (str) -> List[str]
        # TODO: transitively assemble all nodes in our graph that are
        # reachable via internal edges from node
        ret = [node]#set()
        while True:
            l = len(ret)
            self._get_graph_connected_from(node, ret)
            self._get_graph_connected_to(node, ret)
            if len(ret) == l: 
                break

        if len(ret) > 1:
            logging.debug('---> %s is connected to %d nodes: %s'%(node,len(ret),ret))
        # logging.debug('---> Subgraph (%s)'%ret)

        return ret

    def get_graph_connected_from(self,node, ret):
        # type: (str, List[str]) -> None
        # transitively assemble all nodes in our graph that are
        # reachable via internal edges from node
        if node in self.internal_edges:
            for edge in self.internal_edges[node]:
                node2 = edge[1]
                if node2 not in ret:
                    logging.debug('(Found_from %s -> %s)'%(node,node2))
                    ret.append(node2)
                    self._get_graph_connected_from(node2, ret)
                    self._get_graph_connected_to(node2, ret)

        return ret

    def get_graph_connected_to(self,node, ret):
        # type: (str, List[str]) -> None
        # transitively assemble all nodes in our graph that are
        # reachable via internal edges from node
        for node2,edge_list in self.internal_edges.items():
            if node2 not in ret:
                for n in edge_list:
                    if n[1] == node and node2 not in ret:
                        ret.append(node2)
                        logging.debug('(Found_to %s -> %s)'%(node2,n[1]))
                        self._get_graph_connected_from(node2, ret)
                        self._get_graph_connected_to(node2, ret)

        return ret

    def write_self(self, db, resource):
        # type: (cursor, str) -> None
        """
        Clear the write cache, writing any nodes to the DBMS
        """
        logging.info("Writing subgraph with event %s:(%s)" %(self.creation_event, str(self.node_set)))
            #set_id = self.event_manager.find_event_set(db, resource, (node,))
        result = set()
        self.event_manager.get_event_set_from_id(db, resource, result, self.creation_event)#self.event_manager.event_sets[set_id])

        # TODO: this won't be the case any more
        for node in self.node_set:
            self.event_manager.store.add_node_binding(#self.event_sets[set_id]
                self.creation_event,  'label', resource, node)

        # TODO: edges!

    def get_event_expression_id(self):
        # type: (None) -> UUID

        return self.creation_event

    def reclassify_edges(self, db, resource, source, dest):
        # type: (cursor, str, str, str) -> None
        """
        Ensure that any edges that were previously external-facing
        are now internal edges
        """
        remove_these = set()
        for i in range(0, len(self.external_edges)):
            (src,label,dst) = self.external_edges[i]
            if src == source and dst == dest:
                if source in self.internal_edges:
                    self.internal_edges[source].append((label,dest))
                else:
                    self.internal_edges[source] = [(label,dest)]
                remove_these.add((src,label,dst))

        for edge in remove_these:
            self.external_edges.remove(remove_these)
        
        return

    def reclassify_internal_edges(self):
        # type: () -> None
        """
        Ensure that any edges that were previously external-facing
        are now internal edges
        """
        remove_these = set()
        for i in range(0, len(self.external_edges)):
            (src,label,dst) = self.external_edges[i]
            if src in self.node_set and dst in self.node_set:
                if src in self.internal_edges:
                    self.internal_edges[src].append((label,dst))
                else:
                    self.internal_edges[src] = [(label,dst)]
                remove_these.add((src,label,dst))

        for edge in remove_these:
            self.external_edges.remove(remove_these)
        
        return

    def display(self):
        if len(self.node_set):
            logging.debug("** Nodes: **")
            for i in self.node_set:
                logging.debug(' %s' %i)# -> %s'%(i, self.event_sets[self.graph_to_events[(i,)]]))

            if len(self.internal_edges):
                logging.debug("** Internal edges **")
                for i in self.internal_edges:
                    logging.debug(' From %s: %s'%(i,self.internal_edges[i]))

    def set_maximal(self, max):
        # type: (Subgraph) -> None
        self.maximal = max

    def get_maximal(self):
        # type: () -> Subgraph
        return self.maximal

    def get_internal_edges(self):
        if not self.internal_edges:
            self.internal_edges = {}
            
        return self.internal_edges