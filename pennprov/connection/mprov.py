"""
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
"""
from __future__ import print_function

from typing import List, Any, Dict
import hashlib
import binascii
import logging
import re
import pennprov
import datetime
from pennprov.metadata.stream_metadata import BasicTuple

import psycopg2
from pennprov.config import config

from pennprov.connection.dblayer import LogIndex

class MProvConnection:
    graph_name = None
    namespace = 'http://mprov.md2k.org'
    default_host = "localhost"
    QNAME_REGEX = re.compile('{([^}]*)}(.*)')

    #log = LogIndex()
    log = LogIndex.get_index()
    #log = CompressingLogIndex()

    """
    MProvConnection is a high-level API to the PennProvenance framework, with
    a streaming emphasis (i.e., tuples are stored with positions or timestamps,
    and derivations are recorded each time an action is invoked).
    """
    def __init__(self, user=None, password=None, host=None):
        # type: (str, str, str) -> None
        """
        Establish a connection to a PennProvenance server
        :param user: User ID
        :param password: Password for connection
        :param host: Host URL, or None to use localhost
        """
        if user is None:
            user = config.dbms.user

        if password is None:
            password = config.dbms.password

        if host is None:
            host = config.dbms.host

        self.auth_conn = psycopg2.connect(host=host, database=config.dbms.auth_db, user=user, password=password)
        self.graph_conn = psycopg2.connect(host=host, database=config.dbms.graph_db, user=user, password=password)

        self.user_token = self.get_username()

        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                self.log.create_tables(cursor)

        self.graph_name = config.provenance.graph
        return

    def create_or_reset_graph(self):
        print ('Clearing graph...')
        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                self.log.clear_tables(cursor,self.get_graph())
        try:
            self.store_agent(self.get_username())
        except psycopg2.errors.UniqueViolation:
            pass
        self.flush()

    def create_or_reuse_graph(self):
        try:
            self.store_agent(self.get_username())
        except psycopg2.errors.UniqueViolation:
            pass
        self.flush()

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

    def get_username(self):
        return config.provenance.user

    # Create a unique ID for an operator stream window
    @staticmethod
    def get_window_id(stream_operator, wid):
        # type: (str, Any) -> str
        return stream_operator + '_w.' + str(wid)

    # Create a unique ID for a stream operator result
    @staticmethod
    def get_result_id(stream, rid):
        # type: (str, Any) -> str
        return stream + '._r' + str(rid)

    # Create a unique ID for an entity
    @staticmethod
    def get_entity_id(stream, eid=None):
        # type: (str, Any) -> str
        if eid:
            return stream + '._e' + str(eid)
        else:
            return 'e_' + stream

    @staticmethod
    def get_stream_from_entity_id(eid):
        # type: (str) -> str
        if eid.startswith('{'):
            eid = MProvConnection.get_local_part(eid)

        if '._e' in eid:
            return eid[eid.index('._e')+3:]
        elif eid.startswith('e_'):
            return eid[2:]
        else:
            return eid

    # Create a unique ID for an entity
    @staticmethod
    def get_agent_id(user):
        # type: (str) -> str
        return 'u_' + user

    # Create a unique ID for an activity (a stream operator call)
    @staticmethod
    def get_activity_id(operator, aid):
        # type: (str, Any) -> str
        if aid:
            dk = hashlib.pbkdf2_hmac('sha256', (operator+aid).encode('utf-8'), b'prov', 20)

            stream = binascii.hexlify(dk).decode('utf-8')

            return stream#operator + '._a' + str(aid)
        else:
            dk = hashlib.pbkdf2_hmac('sha256', (operator).encode('utf-8'), b'prov', 20)

            stream = binascii.hexlify(dk).decode('utf-8')
            return stream#'a_' + operator

    def get_agent_token(self, agent_name):
        # type (str) -> str
        return  self.get_token_qname(self.get_agent_id(agent_name))

    def store_agent(self, agent_name):
        # type: (str) -> str
        agent_key = self._get_qname(self.user_token)
        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                self.log.add_node(cursor, self.get_graph(), 'AGENT', agent_key)

                key = self._get_qname('agent_name')
                value = self.user_token
                
                self.log.add_nodeprop(cursor, self.get_graph(), agent_key, key, value,0)

        logging.debug('Storing AGENT %s' % str(self.user_token))

        return self.user_token

    def store_activity(self,
                       activity,
                       start,
                       end,
                       location= None):
        # type: (str, int, int, int) -> str
        """
        Create an entity node for an activity (a stream operator computation)

        :param activity: Name of the operation
        :param start: Start time
        :param end: End time
        :param location: Index position etc
        :return:
        """
        node_key = self.get_activity_id(activity,location)#self._get_qname(self.get_activity_id(activity,location))
        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                self.log.add_node(cursor, self.get_graph(), 'ACTIVITY', node_key)

                key = self._get_qname('hash')
                value = activity

                self.log.add_nodeprop(cursor, self.get_graph(), node_key, key, value, 0)

                key = self._get_qname('agent')
                value = self.get_username()

                self.log.add_nodeprop(cursor, self.get_graph(), node_key, key, value, 1)

                self.log.add_edge(cursor, self.get_graph(), node_key, 'wasAssociatedWith', self._get_qname(value))

                key = self._get_qname('provDmStartTime')
                value = datetime.datetime.now()
                self.log.add_nodeprop(cursor, self.get_graph(), node_key, key, value, 2)
                key = self._get_qname('provDmEndTime')
                value = datetime.datetime.now()
                self.log.add_nodeprop(cursor, self.get_graph(), node_key, key, value, 3)

        token = node_key

        logging.debug('Storing ACTIVITY %s with ASSOCIATION %s', str(token), str(self.user_token))

        return token

    def _write_tuple(self, cursor, resource, node, tuple):
        if isinstance(tuple, BasicTuple):
            for i, k in enumerate(tuple.schema.fields):
                v = tuple[k]
                self.log.add_nodeprop(cursor,resource,node,k,v)
                i = i + 1
        else:
            i = 0
            for k,v in tuple.items():
                self.log.add_nodeprop(cursor,self.get_graph(),node,k,v)
                i = i + 1

    def store_stream_tuple(self, stream_name, stream_index, input_tuple):
        # type: (str, int, BasicTuple) -> str

        """
        Create an entity node for a stream tuple

        :param stream_name: The name of the stream itself
        :param stream_index: The index position (count) or timestamp (if unique)
        :param input_tuple: The actual stream value
        :return: token for the new node
        """

        # The "token" for the tuple will be the node ID
        if isinstance(stream_index, int):
            token = self.get_token_qname(self.get_entity_id(stream_name, stream_index - 1))
        else:
            token = self.get_token_qname(self.get_entity_id(stream_name, stream_index))

        # We also embed the token within the tuple, in case the programmer queries the database
        # and wants to see it
        if isinstance(stream_index, int):
            input_tuple[self._get_qname("prov")] = self.get_entity_id(stream_name, stream_index - 1)
        else:
            input_tuple[self._get_qname("prov")] = self.get_entity_id(stream_name, stream_index)

        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                self.log.add_node(cursor, self.get_graph(), 'ENTITY', token)

                self._write_tuple(cursor, self.get_graph(), token, input_tuple)

        logging.debug('Storing ENTITY ' + str(token))

        return token

    def store_code(self, code):
        # type: (str) -> str

        """
        Store a code definition as an entity

        :param code: Source code definition
        :return: String ID (local part of QName) for the node
        """

        dk = hashlib.pbkdf2_hmac('sha256', code.encode('utf-8'), b'mprov', 10000)

        stream = binascii.hexlify(dk).decode('utf-8')

        # The "token" for the tuple will be the node ID
        token = self.get_entity_id(stream)

        # Now we'll create a tuple within the provenance node, to capture the data
        data = {self._get_qname("prov"): token, 'code': code, 'type': 'python3'}

        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                self.log.add_node(cursor, self.get_graph(), 'ENTITY', token)

                self._write_tuple(cursor, self.get_graph(), token, data)

        logging.debug('Storing ENTITY ' + str(token))

        return token

    def store_annotations(self,
                          node_token,
                          annotation_dict):
        # type: (str, dict) -> List[str]
        """
        Associate a map of annotations with a node ID

        :param node_token:
        :param annotation_dict:
        :return:
        """

        ann_tokens = []

        for k in annotation_dict.keys():
            ann_token = self.get_token_qname(MProvConnection.get_local_part(node_token) + "." + k)
            ann_tokens.append(ann_token)

            # The key/value pair will itself be an entity node
            attributes = {k: annotation_dict[k]}
            self._write_annot(ann_token, node_token, attributes)

        return ann_tokens

    def _write_annot(self, ann_token, node_token, attributes):
        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                self.log.add_node(cursor, self.get_graph(), 'ENTITY', ann_token)
                # Then we add a relationship edge (of type ANNOTATED)
                self.log.add_edge(cursor, self.get_graph(), ann_token, '_annotated', node_token)
                logging.debug('Wrote ANNOT edge %s' % ann_token)

                # Write the annotation tuple
                self._write_tuple(cursor, self.get_graph(), ann_token, attributes)


    def store_annotation(self,
                         stream_name,
                         stream_index,
                         annotation_name,
                         annotation_value):
        # type: (str, int, str, Any) -> str
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
        node_token = self.get_token_qname(self.get_entity_id(stream_name, stream_index - 1))

        ann_token = self.get_token_qname(self.get_entity_id(stream_name + '.' + annotation_name, stream_index - 1))

        # The key/value pair will itself be an entity node
        attributes = {annotation_name: annotation_value}

        self._write_annot(ann_token, node_token, attributes)

        return ann_token

    def store_window_and_inputs(self,
                                output_stream_name,
                                output_stream_index,
                                input_tokens_list
                                ):
        # type: (str, int, list) -> str
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
            window_token = self.get_token_qname(self.get_window_id(output_stream_name, output_stream_index - 1))
        else:
            window_token = self.get_token_qname(self.get_window_id(output_stream_name, output_stream_index))

        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                self.log.add_node(cursor, self.get_graph(), 'COLLECTION', window_token)

                logging.debug('Storing COLLECTION %s' % str(window_token))

                for token in input_tokens_list:
                    # Add a relationship edge (of type ANNOTATED)
                    # from window to its inputs
                    token_qname = self.get_token_qname(token)

                    self.log.add_edge(cursor, self.get_graph(), window_token, 'hadMember', token_qname)

        return window_token

    def store_derived_result(self,
                             output_stream_name,
                             output_stream_index,
                             output_tuple,
                             input_token,
                             activity,
                             start,
                             end
                             ):
        # type: (str, int, BasicTuple, list, str, int, int) -> str
        """
        When we have a windowed computation, this creates a complex derivation subgraph
        in one operation.

        :param output_stream_name: The name of the stream our operator produces
        :param output_stream_index: The position of the outgoing tuple in the stream
        :param output_tuple: The tuple itself
        :param input_token: IDs of the inputs to the computation
        :param activity: The computation name
        :param start: Start time
        :param end: End time
        :return:
        """
        result_token = self.store_stream_tuple(output_stream_name, output_stream_index, output_tuple)

        activity_token = self.store_activity(activity, start, end, output_stream_index)

        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                self.log.add_edge(cursor, self.get_graph(), result_token, 'wasDerivedFrom', input_token)
                self.log.add_edge(cursor, self.get_graph(), activity_token, 'used', input_token)
                self.log.add_edge(cursor, self.get_graph(), result_token, 'wasGeneratedBy', activity_token)

        logging.debug('Storing DERIVATION %s', result_token)
        return result_token

    def create_collection(self,
                          collection_name, collection_version=None,
                          prior_token=None):
        # type: (str, int, str) -> str
        """
        We can create a collection to represent a sub-sequence, a sub-stream, or a subset of items

        :param collection_name:
        :param collection_version:
        :param prior_token:
        :return:
        """
        token = self.get_token_qname(self.get_entity_id(collection_name, collection_version))

        # Create a node for the collection
        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                self.log.add_node(cursor, self.get_graph(), 'COLLECTION', token)

        if prior_token:
            with self.graph_conn as conn:
                with conn.cursor() as cursor:
                    self.log.add_edge(cursor, self.get_graph(), token, 'wasDerivedFrom', prior_token)

        return token

    def add_to_collection(self, tuple_token, collection_token):
        # type (str, str) -> str
        """
        Associate a tuple with a collection (using the tokens for each)

        :param tuple_token:
        :param collection_token:
        :return:
        """
        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                self.log.add_edge(cursor, self.get_graph(), collection_token, 'hadMember', tuple_token)

    def store_windowed_result(self,
                              output_stream_name,
                              output_stream_index,
                              output_tuple,
                              input_tokens_list,
                              activity,
                              start,
                              end
                              ):
        # type: (str, int, BasicTuple, list, str, int, int) -> str
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

        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                self.log.add_edge(cursor, self.get_graph(), result_token, 'wasDerivedFrom', window_token)
                self.log.add_edge(cursor, self.get_graph(), activity_token, 'used', window_token)
                self.log.add_edge(cursor, self.get_graph(), result_token, 'wasGeneratedBy', activity_token)

        return result_token

    def store_derived_from(self, derived_node, source_node):
        # types: (str, str) -> str
        """
        Stores a derivation of an output from an input
        :param derived_node:
        :param source_node:
        :return:
        """
        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                self.log.add_edge(cursor, self.get_graph(), derived_node, 'wasDerivedFrom', source_node)

    def store_used(self, activity_node, input_node):
        # types: (str, str) -> str
        """
        Stores a usage relationship between an activity and an input
        :param activity_node:
        :param input_node:
        :return:
        """
        self.log.add_edge(self.graph_conn.cursor(), self.get_graph(), activity_node, 'used', input_node)

    def store_generated_by(self, output_node, activity_node):
        # types: (str, str) -> str
        """
        Stores an edge indicating an output was generated by an activity
        :param self:
        :param output_node:
        :param activity_node:
        :return:
        """
        self.log.add_edge(self.graph_conn.cursor(), self.get_graph(), output_node, 'wasGeneratedBy', activity_node)

    def _get_qname(self, local_part):
        # types: (str) -> str
        """
        Returns a qualified name from a string to be used as the local part
        :param local_part:
        :return:
        """
        return "{" + self.namespace + "}" + local_part

    def get_token_qname(self, token):
        # types: (str) -> str
        """
        Returns a qualified name created by hashing the given token. Used for cases where the length of
        the resulting name needs to be of limited length, for example when creating a prov token.
        :param token:
        :return:
        """
        if len(token) > 40:
            thash = hashlib.sha1(token.encode('utf-8'))
            return self._get_qname(thash.hexdigest())
        else:
            return self._get_qname(token)

    def get_node(self, entity_id):
        # type: (str) -> List[Dict]
        """
        Returns the tuple data associated with a node ID (generally an entity node)
        :param entity_id:
        :return:
        """
        result = self.get_provenance_data(self.get_graph(), (entity_id))

        return result

    def get_source_entities(self, entity_id):
        # type: (str) -> List[str]
        """
        Given an entity node, what was it derived from?
        :param entity_id:
        :return:
        :param entity_id:
        :return:
        """
        results = self.get_connected_from(self.get_graph(), (entity_id), 'wasDerivedFrom')
        # results = [self.parse_qname(tok.token_value) for tok in results.tokens]
        return results

    def get_derived_entities(self, entity_id):
        # type: (str) -> List[str]
        results = self.get_connected_to(self.get_graph(), (entity_id), 'wasDerivedFrom')

        return results

    def get_parent_entities(self, entity_id):
        # type: (str) -> List[str]
        """
        Find a parent collection (ie a node where this node is a member)
        :param entity_id:
        :return:
        """
        results = self.get_connected_to(self.get_graph(), (entity_id), 'hadMember')
        # results = [self.parse_qname(tok.token_value) for tok in results.tokens]
        return results

    def get_child_entities(self, entity_id):
        # type: (str) -> List[str]
        """
        Find any child (member) nodes
        :param entity_id:
        :return:
        """
        results = self.get_connected_from(self.get_graph(), (entity_id), 'hadMember')
        # results = [self.parse_qname(tok.token_value) for tok in results.tokens]
        return results

    def get_creating_activities(self, entity_id):
        # type: (str) -> List[str]
        """
        Get the list of activities that from which this output was generated
        :param entity_id:
        :return:
        """
        results = self.get_connected_from(self.get_graph(), (entity_id), 'wasGeneratedBy')

        return results

    def get_activity_outputs(self, activity_id):
        # type: (str) -> List[str]
        """
        Get the list of entities this activity generated
        :param activity_id:
        :return:
        """
        results = self.get_connected_to(self.get_graph(), (activity_id), 'wasGeneratedBy')
        return results

    def get_activity_inputs(self, activity_id):
        # type: (str) -> List[str]
        """
        Given an activity, what inputs did it use?
        :param activity_id:
        :return:
        """
        results = self.get_connected_from(self.get_graph(), (activity_id), 'used')
        # results = [self.parse_qname(tok.token_value) for tok in results.tokens]
        return results

    def get_annotations(self, node_id):
        # type: (str) -> List[dict]
        """
        Given a node, find its annotations and return as a list of typed key/values
        :param node_id:
        :return:
        """
        results = self.get_connected_to(self.get_graph(), (node_id), '_annotated')

        results = [self.get_node(eid) for eid in results]

        return results

    def get_stream_inputs(self, stream_name):
        # type: (str) -> List[str]
        inputs = []

        stream_node = self.get_token_qname(self.get_entity_id(stream_name))

        for node in self.get_source_entities(stream_node):
            inputs.append(self.get_stream_from_entity_id(MProvConnection.get_local_part(node)))

        return inputs

    def get_stream_producers(self, stream_name):
        # type: (str) -> List[str]
        producers = []
        stream_node = self.get_token_qname(self.get_entity_id(stream_name))

        for node in self.get_creating_activities(stream_node):
            code = self.get_node(node)

            if len(code) > 0:
                code_id  = code[0][0]#[self._get_qname('hash')]
                #print(code_id)
                code = self.get_node(code_id)#self.get_token_qname(code_id))
                producers.append(self._get_qname(code[0]['code']))

        return producers

    @classmethod
    def get_local_part(cls, token_value):
        # type: (str) -> str
        """
        Returns a QualifiedName by parsing the given string as a namespace and local part
        :param token_value: a string of the form '{' + namespace + '}' + local_part
        :return: the corresponding local portion of the name
        """
        match = cls.QNAME_REGEX.match(token_value)
        if not match:
            raise ValueError('cannot parse as QualfiedName:', token_value)
        return match.group(2)

    def get_provenance_data(self, resource, token):
        # type: (str, str) -> List[Dict]
        self.flush()
        ret = []
        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                return self.log.get_provenance_data(cursor, resource, token)

    def get_connected_to(self, resource, token, label1):
        # type: (str, str, str) -> List[pennprov.ProvTokenSetModel]
        self.flush()
        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                return self.log.get_connected_to(cursor, resource, token, label1)

    def get_connected_from(self, resource, token, label1):
        # type: (str, str, str) -> List[pennprov.ProvTokenSetModel]
        self.flush()
        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                return self.log.get_connected_from(cursor, resource, token, label1)

    def flush(self):
        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                self.log.flush(cursor)
            conn.commit()
        return

    def close(self):
        self.flush()
        return

    def __del__(self):
        self.close()
    