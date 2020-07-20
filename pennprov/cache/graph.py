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

class GraphCache:
    graph_name = ''
    nodes = {}
    edges = []
    edges_from = {}
    edges_to = {}
    prov_api = None
    prov_dm_api = None
    local_only = True

    MAX = 10000

    pending_writes = []

    def __init__(self, graph, prov_api, prov_dm_api):
        # type: (str, pennprov.ProvenanceApi, pennprov.ProvDmApi) -> None

        self.graph_name = graph
        self.prov_api = prov_api
        self.prov_dm_api = prov_dm_api

    def _append(self, item):
        self.pending_writes.append(item)
        if len(self.pending_writes) > self.MAX:
            self.flush()

    def store_node(self, resource, token, body):
        # type: (str, pennprov.QualifiedName, pennprov.NodeModel) -> pennprov.QualifiedName

        self.nodes[token.local_part] = body
        self.edges_from[token.local_part] = []
        self.edges_to[token.local_part] = []
        self._append(lambda: self.prov_dm_api.store_node(resource, token, self.nodes[token.local_part]))
        return token

    def store_relation(self, resource, body, label):
        # type: (str, pennprov.RelationModel, str) -> None

        inx = len(self.edges)
        self.edges.append((label, body))
        self.edges_from[body.subject_id.local_part].append(inx)
        self.edges_to[body.subject_id.local_part].append(inx)
        self._append(lambda: self.prov_dm_api.store_relation(resource, self.edges[inx][1], label))

    def get_connected_to(self, resource, token, label1):
        # type: (str, pennprov.QualifiedName, str) -> List[pennprov.ProvTokenSetModel]

        if self.local_only:
            results = [self.edges[i][1].object_id for i in self.edges_to[token.local_part] if self.edges[i][0] == label1]
        else:
            results = self.prov_api.get_connected_to(resource, token, label=label1)
            results = [pennprov.connection.mprov_connection.MProvConnection.parse_qname(tok.token_value) for tok in results.tokens]

        return results

    def get_connected_from(self, resource, token, label1):
        # type: (str, pennprov.QualifiedName, str) -> List[pennprov.ProvTokenSetModel]

        if self.local_only:
            results = [self.edges[i][1].object_id for i in self.edges_from[token.local_part] if self.edges[i][0] == label1]
        else:
            results = self.prov_api.get_connected_from(resource, token, label=label1)
            results = [pennprov.connection.mprov_connection.MProvConnection.parse_qname(tok.token_value) for tok in results.tokens]

        return results

    def get_provenance_data(self, resource, token):
        # type: (str, pennprov.QualifiedName) -> List[Dict]

        if self.local_only:
            self.flush()

        result = self.prov_api.get_provenance_data(resource, (token))
        ret = [{d.to_dict()['name'].split('}')[-1]: d.to_dict()['value'], 'type': d.to_dict()['type']} for d in
               result.tuple if d.to_dict()['name'].split('}')[-1] != 'provDmName']

        return ret

    def flush(self):
        for fn in self.pending_writes:
            fn()
        self.pending_writes = []
        self.local_only = False

    def close(self):
        self.flush()