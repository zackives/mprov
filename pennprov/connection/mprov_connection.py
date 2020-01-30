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
from pprint import pprint

import logging
import pennprov
from pennprov.rest import ApiException
from pennprov.metadata.stream_metadata import BasicSchema, BasicTuple


class MProvConnection:
    """
    MProvConnection is a high-level API to the PennProvenance framework, with
    a streaming emphasis (i.e., tuples are stored with positions or timestamps,
    and derivations are recorded each time an action is invoked).
    """

    namespace = 'http://mprov.md2k.org'
    graph_name = "mProv-graph"

    def __init__(self, user, password, host):
        # type: (str, str, str) -> None
        """
        Establish a connection to a PennProvenance server
        :param user: User ID
        :param password: Password for connection
        :param host: Host URL, or None to use localhost
        """
        self.configuration = pennprov.configuration.Configuration()
        if host:
            self.configuration.host = host
        else:
            self.configuration.host = "http://localhost:8088"

        api_client = pennprov.ApiClient(self.configuration)
        self.auth_api = pennprov.AuthenticationApi(api_client)
        self.prov_api = pennprov.ProvenanceApi(api_client)
        self.prov_dm_api = pennprov.ProvDmApi(api_client)
        self.username = user
        credentials = pennprov.UserCredentials(password)

        # One-time initialization of client with a JWT token for
        # authentication.
        web_token = self.auth_api.get_token_route(self.username, credentials)
        self.token = web_token.token

        self.configuration.api_key["api_key"] = self.token

        self.prov_api.create_or_reset_provenance_graph(self.get_graph())
        return

    def get_graph(self):
        """
        Within the storage system, get the name of the graph
        :return:
        """
        return self.graph_name

    def set_graph(self, name):
        """
        Set the name of the graph in the graph store
        :param name:
        :return:
        """
        self.graph_name = name

    def get_provenance_store(self):
        return self.prov_dm_api

    def get_low_level_api(self):
        return self.prov_api

    def get_auth_api(self):
        return self.auth_api

    def get_username(self):
        return self.username

    # Create a unique ID for an operator stream window
    def get_window_id(self, stream_operator, id):
        # type: (str, Any) -> str
        return stream_operator + '_w.' + str(id)

    # Create a unique ID for a stream operator result
    def get_result_id(self, stream, id):
        # type: (str, Any) -> str
        return stream + '._r' + str(id)

    # Create a unique ID for an entity
    def get_entity_id(self, stream, id):
        # type: (str, Any) -> str
        return stream + '._e' + str(id)

    # Create a unique ID for an activity (a stream operator call)
    def get_activity_id(self, operator, id):
        # type: (str, Any) -> str
        return operator + '._e' + str(id)

    def store_activity(self,
                       activity,
                       start,
                       end,
                       location):
        # type: (str, int, int, int) -> None
        """
        Create an entity node for an activity (a stream operator computation)

        :param activity: Name of the operation
        :param start: Start time
        :param end: End time
        :param location: Index position etc
        :return:
        """
        data = []

        tok = pennprov.ProvTokenModel(token_value=self.get_activity_id('activity', location))
        token = pennprov.QualifiedName(self.namespace, self.get_activity_id(activity, location))
        activity = pennprov.NodeModel(type='ACTIVITY', attributes=data, \
                                      location=tok, start_time=start, end_time=end)
        self.prov_dm_api.store_node(resource=self.get_graph(),
                                    token=token, body=activity)
        logging.debug('Storing ACTIVITY %s' % str(token))

        return token

    def store_stream_tuple(self, stream_name, stream_index, input_tuple):
        # type: (str, int, BasicTuple) -> pennprov.QualifiedName

        """
        Create an entity node for a stream tuple

        :param stream_name: The name of the stream itself
        :param stream_index: The index position (count) or timestamp (if unique)
        :param input_tuple: The actual stream value
        :return: token for the new node
        """

        # The "token" for the tuple will be the node ID
        if isinstance(stream_index, int):
            token = pennprov.QualifiedName(self.namespace, self.get_entity_id(stream_name, stream_index - 1))
        else:
            token = pennprov.QualifiedName(self.namespace, self.get_entity_id(stream_name, stream_index))

        # We also embed the token within the tuple, in case the programmer queries the database
        # and wants to see it
        if isinstance(stream_index, int):
            input_tuple["_prov"] = self.get_entity_id(stream_name, stream_index - 1)
        else:
            input_tuple["_prov"] = self.get_entity_id(stream_name, stream_index)

        # Now we'll create a tuple within the provenance node, to capture the data
        data = []
        for i, k in enumerate(input_tuple.schema.fields):
            qkey = pennprov.QualifiedName(self.namespace, k)
            data.append(pennprov.Attribute(name=qkey, value=input_tuple[i], type='STRING'))

        # Finally, we build an entity node within the graph, with the token and the
        # attributes
        entity_node = pennprov.NodeModel(type='ENTITY', attributes=data)
        self.prov_dm_api.store_node(resource=self.get_graph(),
                                    token=token, body=entity_node)

        logging.debug('Storing ENTITY ' + str(token))

        return token

    def store_annotation(self,
                         stream_name,
                         stream_index,
                         annotation_name,
                         annotation_value):
        # type: (str, int, str, Any) -> pennprov.QualifiedName
        """
        Create a node for an annotation to an entity / tuple

        :param stream_name: The name of the stream itself
        :param stream_index: The index position (count) or timestamp (if unique) of the
                stream element we are annotating
        :param annotation_name: The name of the annotation
        :param annotation_value: The value of the annotation
        :return:
        """

        # The "token" for the tuple will be the node ID
        token = pennprov.QualifiedName(self.namespace, self.get_entity_id(stream_name, stream_index - 1))

        ann_token = pennprov.QualifiedName(self.namespace,
                                           self.get_entity_id(stream_name + '.' + annotation_name, stream_index - 1))

        # The key/value pair will itself be an entity node
        attributes = [
            pennprov.Attribute(name=pennprov.QualifiedName(self.namespace, annotation_name), value=annotation_value,
                               type='STRING')]
        entity_node = pennprov.NodeModel(type='ENTITY', attributes=attributes)
        self.prov_dm_api.store_node(resource=self.get_graph(),
                                    token=ann_token, body=entity_node)

        # Then we add a relationship edge (of type ANNOTATED)
        annotates = pennprov.RelationModel(
            type='ANNOTATED', subject_id=token, object_id=ann_token, attributes=[])
        self.prov_dm_api.store_relation(resource=self.get_graph(), body=annotates, label='_annotated')

        return ann_token

    def store_window_and_inputs(self,
                                output_stream_name,
                                output_stream_index,
                                input_tokens_list
                                ):
        # type: (str, int, list) -> pennprov.QualifiedName
        """
        Store a mapping between an operator window, from
        which a stream is to be derived, and the input
        nodes

        :param output_stream_name:
        :param output_stream_index:
        :param input_tokens_list:
        :return:
        """

        # The "token" for the tuple will be the node ID
        if isinstance(output_stream_index, int):
            window_token = pennprov.QualifiedName(self.namespace,
                                                  self.get_window_id(output_stream_name, output_stream_index - 1))
        else:
            window_token = pennprov.QualifiedName(self.namespace,
                                                  self.get_window_id(output_stream_name, output_stream_index))

        # Finally, we build an entity node within the graph, with the token and the
        # attributes
        coll_node = pennprov.NodeModel(type='COLLECTION', attributes=[])
        self.prov_dm_api.store_node(resource=self.get_graph(),
                                    token=window_token, body=coll_node)

        logging.debug('Storing COLLECTION %s' % str(window_token))

        for token in input_tokens_list:
            # Add a relationship edge (of type ANNOTATED)
            # from window to its inputs
            token_qname = pennprov.QualifiedName(self.namespace, token)
            annotates = pennprov.RelationModel(
                type='MEMBERSHIP', subject_id=token_qname, object_id=window_token, attributes=[])

            self.prov_dm_api.store_relation(resource=self.get_graph(), body=annotates, label='membership')

        return window_token

    def store_windowed_result(self,
                              output_stream_name,
                              output_stream_index,
                              output_tuple,
                              input_tokens_list,
                              activity,
                              start,
                              end
                              ):
        # type: (str, int, BasicTuple, list, str, int, int) -> pennprov.QualifiedName
        """
        When we have a windowed computation, this creates a complex derivation subgraph
        in one operation.

        :param output_stream_name: The name of the stream our operator produces
        :param output_stream_index: The position of the outgoing tuple in the stream
        :param output_tuple: The tuple itself
        :param input_tokens_list: IDs of the inputs to the computation
        :param activity: The computation name
        :param start: Start time
        :param end: End time
        :return:
        """
        result_token = self.store_stream_tuple(output_stream_name, output_stream_index, output_tuple)
        window_token = self.store_window_and_inputs(output_stream_name, output_stream_index, input_tokens_list)

        activity_token = self.store_activity(activity, start, end, output_stream_index)

        derives = pennprov.RelationModel(
            type='DERIVATION', subject_id=result_token, object_id=window_token, attributes=[])
        self.prov_dm_api.store_relation(resource=self.get_graph(), body=derives, label='derivation')

        uses = pennprov.RelationModel(
            type='USAGE', subject_id=activity_token, object_id=window_token, attributes=[])
        self.prov_dm_api.store_relation(resource=self.get_graph(), body=uses, label='usage')

        generates = pennprov.RelationModel(
            type='GENERATION', subject_id=activity_token, object_id=result_token, attributes=[])
        self.prov_dm_api.store_relation(resource=self.get_graph(), body=generates, label='generation')

        return window_token
