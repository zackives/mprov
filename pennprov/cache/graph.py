"""
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
"""
from __future__ import print_function
import pennprov
from typing import List, Any, Dict
import cachetools

class GraphCache:
    graph_name = ''
    prov_api = None
    prov_dm_api = None

    MAX = 10000

    pending_writes = []

    def __init__(self, graph, prov_api, prov_dm_api, ttl_seconds=2, max_cache_size=None):
        # type: (str, pennprov.ProvenanceApi, pennprov.ProvDmApi, int) -> None
        maxsize = max_cache_size or float('inf')
        self.graph_name = graph
        self.prov_api = prov_api
        self.prov_dm_api = prov_dm_api
        # node_id.local_part -> NodeModel
        self.nodes = cachetools.TTLCache(maxsize=maxsize, ttl=ttl_seconds)
        # (subject_id.local_part, label, object_id.local_part) -> RelationModel
        self.edges = cachetools.TTLCache(maxsize=maxsize, ttl=ttl_seconds)
        # node_id.local_part -> List[Dict]
        self.prov_data = cachetools.TTLCache(maxsize=maxsize, ttl=ttl_seconds)
        # (subject_id.local_part, label) -> List[object_id]
        self.connected_from = cachetools.TTLCache(maxsize=maxsize, ttl=ttl_seconds)
        # (object_id.local_part, label) -> List[subject_id]
        self.connected_to = cachetools.TTLCache(maxsize=maxsize, ttl=ttl_seconds)

    def _append(self, item):
        self.pending_writes.append(item)
        if len(self.pending_writes) > self.MAX:
            self.flush()

    def store_node(self, resource, token, body):
        # type: (str, pennprov.QualifiedName, pennprov.NodeModel) -> pennprov.QualifiedName

        if token.local_part not in self.nodes:
            self.nodes[token.local_part] = body
            self._append(lambda: self.prov_dm_api.store_node(resource, token, body))
        return token

    def store_relation(self, resource, body, label):
        # type: (str, pennprov.RelationModel, str) -> None
        edge_key = (body.subject_id.local_part, label, body.object_id.local_part)

        if edge_key in self.edges:
            return

        self.edges[edge_key] = body
        
        connected_from_key = (body.subject_id.local_part, label)
        connected_from = self.connected_from.get(connected_from_key)
        if not connected_from:
            connected_from = []
            self.connected_from[connected_from_key] = connected_from
        connected_from.append(body.object_id)

        connected_to_key = (body.object_id.local_part, label)
        connected_to = self.connected_to.get(connected_to_key)
        if not connected_to:
            connected_to = []
            self.connected_to[connected_to_key] = connected_to
        connected_to.append(body.subject_id)

        self._append(lambda: self.prov_dm_api.store_relation(resource, body, label))
        self.flush()

    def get_connected_to(self, resource, token, label1):
        # type: (str, pennprov.QualifiedName, str) -> List[pennprov.ProvTokenSetModel]

        key = (token.local_part, label1)
        subject_ids = self.connected_to.get(key)

        if not subject_ids:
            self.flush()
            from_server = self.prov_api.get_connected_to(resource, token, label=label1)
            subject_ids = [pennprov.connection.mprov_connection.MProvConnection.parse_qname(tok.token_value) for tok in from_server.tokens]
            self.connected_to[key] = subject_ids

        return subject_ids

    def get_connected_from(self, resource, token, label1):
        # type: (str, pennprov.QualifiedName, str) -> List[pennprov.ProvTokenSetModel]
        key = (token.local_part, label1)
        object_ids = self.connected_from.get(key)
        
        if not object_ids:
            self.flush()
            from_server = self.prov_api.get_connected_from(resource, token, label=label1)
            object_ids = [pennprov.connection.mprov_connection.MProvConnection.parse_qname(tok.token_value) for tok in from_server.tokens]
            self.connected_from[key] = object_ids

        return object_ids

    def get_provenance_data(self, resource, token):
        # type: (str, pennprov.QualifiedName) -> List[Dict]

        ret = self.prov_data.get(token.local_part)
        if not ret:
            self.flush()
            result = self.prov_api.get_provenance_data(resource, (token))
            ret = [{d.to_dict()['name'].split('}')[-1]: d.to_dict()['value'], 'type': d.to_dict()['type']} for d in
                result.tuple if d.to_dict()['name'].split('}')[-1] != 'provDmName']
            self.prov_data[token.local_part] = ret

        return ret

    def flush(self):
        for fn in self.pending_writes:
            fn()
        self.pending_writes = []

    def close(self):
        self.flush()
        