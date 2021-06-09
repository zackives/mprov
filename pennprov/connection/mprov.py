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

from typing import List, Any
import hashlib
import binascii
import logging
import re
import pennprov
from pennprov.metadata.stream_metadata import BasicTuple

#from pennprov.cache.graph import GraphCache

import psycopg2
from pennprov.config import config

class MProvConnection:
    cache = None
    graph_name = None

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

        print(self.graph_conn)
        print(self.auth_conn)

        self._create_tables()
        self.graph_name = config.provenance.graph
        return

    def _create_tables(self):
        """
        Create the graph relations if need be
        """

        node_table = """
                     CREATE TABLE IF NOT EXISTS MProv_Node(_key VARCHAR(80) NOT NULL,
                                                           _resource VARCHAR(80) NOT NULL,
                                                           _created SERIAL,
                                                           label VARCHAR(80),
                                                           PRIMARY KEY(_resource, _key))
                     """

        node_props_table = """
                     CREATE TABLE IF NOT EXISTS MProv_NodeProp(_key VARCHAR(80) NOT NULL,
                                                           _resource VARCHAR(80) NOT NULL,
                                                           type VARCHAR(80),
                                                           label VARCHAR(80),
                                                           value VARCHAR,
                                                           code CHAR(1),
                                                           ivalue INTEGER,
                                                           lvalue BIGINT,
                                                           dvalue DOUBLE PRECISION,
                                                           fvalue REAL,
                                                           tvalue DATE,
                                                           index BIGINT,
                                                           PRIMARY KEY(_resource, _key, label),
                                                           UNIQUE(_resource,_key,index),
                                                           FOREIGN KEY(_resource,_key) REFERENCES MProv_Node
                                                             ON DELETE CASCADE)
                           """

        edge_table = """
                     CREATE TABLE IF NOT EXISTS MProv_Edge(_key SERIAL,
                                                           _resource VARCHAR(80) NOT NULL,
                                                           _from VARCHAR(80) NOT NULL,
                                                           _to VARCHAR(80) NOT NULL,
                                                           label VARCHAR(80),
                                                           PRIMARY KEY(_resource, _key),
                                                           UNIQUE(_resource, _from, _to, label),
                                                           FOREIGN KEY(_resource, _from) REFERENCES MProv_Node
                                                            ON DELETE CASCADE,
                                                           FOREIGN KEY(_resource, _to) REFERENCES MProv_Node
                                                            ON DELETE CASCADE)
                     """

        edge_props_table = """
                     CREATE TABLE IF NOT EXISTS MProv_EdgeProp(_key INTEGER NOT NULL,
                                                           _resource VARCHAR(80) NOT NULL,
                                                           _created SERIAL,
                                                           type VARCHAR(80),
                                                           label VARCHAR(80),
                                                           value VARCHAR,
                                                           code CHAR(1),
                                                           ivalue INTEGER,
                                                           lvalue BIGINT,
                                                           dvalue DOUBLE PRECISION,
                                                           fvalue REAL,
                                                           tvalue DATE,
                                                           index BIGINT,
                                                           PRIMARY KEY(_resource, _key, label),
                                                           UNIQUE(_resource,_key,index),
                                                           FOREIGN KEY(_resource,_key) REFERENCES MProv_Edge
                                                             ON DELETE CASCADE)
                           """

        schema_table = """
                     CREATE TABLE IF NOT EXISTS MProv_Schema(_key VARCHAR(80) NOT NULL,
                                                           _resource VARCHAR(80) NOT NULL,
                                                           name VARCHAR(80) NOT NULL,
                                                           value VARCHAR,
                                                           PRIMARY KEY(_resource, _key),
                                                           UNIQUE(_resource, name))
                       """

        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(node_table)
                cursor.execute(node_props_table)
                cursor.execute(edge_table)
                cursor.execute(edge_props_table)
                cursor.execute(schema_table)
        return
    
    def create_or_reset_graph(self):
        self.prov_api.create_or_reset_provenance_graph(self.get_graph())
        self.user_token = self.store_agent(self.config.provenance.user)
        self.flush()

    def create_or_reuse_graph(self):
        self.prov_api.create_provenance_graph(self.get_graph())
        self.user_token = self.store_agent(self.config.provenance.user)
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

    def get_provenance_store(self):
        return self.prov_dm_api

    def get_low_level_api(self):
        return self.prov_api

    def get_auth_api(self):
        return self.auth_api

    def get_username(self):
        return self.config.provenance.user

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
        if isinstance(eid, pennprov.QualifiedName):
            eid = eid.local_part

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
            return operator + '._a' + str(aid)
        else:
            return 'a_' + operator

    def get_agent_token(self, agent_name):
        # type (str) -> pennprov.QualifiedName
        return  self.get_token_qname(self.get_agent_id(agent_name))

    def store_agent(self, agent_name):
        # type: (str) -> pennprov.QualifiedName

        data = []
        data.append(pennprov.Attribute(name=self._get_qname('uname'), value=agent_name, type='STRING'))

        agent = pennprov.NodeModel(type='AGENT', attributes=data)
        self.cache.store_node(resource=self.get_graph(),
                              token=self.user_token, body=agent)
        logging.debug('Storing AGENT %s' % str(self.user_token))

        return self.user_token

    def store_activity(self,
                       activity,
                       start,
                       end,
                       location= None):
        # type: (str, int, int, int) -> pennprov.QualifiedName
        """
        Create an entity node for an activity (a stream operator computation)

        :param activity: Name of the operation
        :param start: Start time
        :param end: End time
        :param location: Index position etc
        :return:
        """
        data = []
        data.append(pennprov.Attribute(name=self._get_qname('hash'), value=activity, type='STRING'))
        data.append(pennprov.Attribute(name=self._get_qname('agent'), value=self.config.provenance.user, type='STRING'))

        tok = pennprov.ProvTokenModel(token_value=self.get_activity_id('activity', location))
        token = self.get_token_qname(self.get_activity_id(activity, location))
        activity = pennprov.NodeModel(type='ACTIVITY', attributes=data,
                                      location=tok, start_time=start, end_time=end)
        self.cache.store_node(resource=self.get_graph(),
                              token=token, body=activity)

        data2 = []

        data.append(pennprov.Attribute(name=pennprov.QualifiedName('prov', 'role'), value='loggedInUser', type='STRING'))
        # Then we add a relationship edge (of type ANNOTATED)
        association = pennprov.RelationModel(
            type='ASSOCIATION', subject_id=token, object_id=self.user_token, attributes=data2)
        self.cache.store_relation(resource=self.get_graph(), body=association, label='wasAssociatedWith')
        logging.debug('Storing ACTIVITY %s with ASSOCIATION %s', str(token), str(self.user_token))

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
            token = self.get_token_qname(self.get_entity_id(stream_name, stream_index - 1))
        else:
            token = self.get_token_qname(self.get_entity_id(stream_name, stream_index))

        # We also embed the token within the tuple, in case the programmer queries the database
        # and wants to see it
        if isinstance(stream_index, int):
            input_tuple["_prov"] = self.get_entity_id(stream_name, stream_index - 1)
        else:
            input_tuple["_prov"] = self.get_entity_id(stream_name, stream_index)

        # Now we'll create a tuple within the provenance node, to capture the data
        data = []
        for i, k in enumerate(input_tuple.schema.fields):
            qkey = self.get_token_qname(k)
            data.append(pennprov.Attribute(name=qkey, value=input_tuple[k], type='STRING'))

        # Finally, we build an entity node within the graph, with the token and the
        # attributes
        entity_node = pennprov.NodeModel(type='ENTITY', attributes=data)
        self.cache.store_node(resource=self.get_graph(),
                              token=token, body=entity_node)

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
        data = []
        data.append(pennprov.Attribute(name=self._get_qname('prov'), value=token, type='STRING'))
        data.append(pennprov.Attribute(name=self._get_qname('code'), value=code, type='STRING'))
        data.append(pennprov.Attribute(name=self._get_qname('type'), value='python3', type='STRING'))

        # Finally, we build an entity node within the graph, with the token and the
        # attributes
        entity_node = pennprov.NodeModel(type='ENTITY', attributes=data)
        self.cache.store_node(resource=self.get_graph(),
                              token=self.get_token_qname(token), body=entity_node)

        logging.debug('Storing ENTITY ' + str(token))

        return token

    def store_annotations(self,
                          node_token,
                          annotation_dict):
        # type: (pennprov.QualifiedName, dict) -> List[pennprov.QualifiedName]
        """
        Associate a map of annotations with a node ID

        :param node_token:
        :param annotation_dict:
        :return:
        """

        ann_tokens = []

        for k in annotation_dict.keys():
            ann_token = self.get_token_qname(node_token.local_part + "." + k)
            ann_tokens.append(ann_token)

            # The key/value pair will itself be an entity node
            attributes = [
                pennprov.Attribute(name=self.get_token_qname(k), value=annotation_dict[k],
                                   type='STRING')]
            self._write_annot(ann_token, node_token, attributes)

        return ann_tokens

    def _write_annot(self, ann_token, node_token, attributes):
        entity_node = pennprov.NodeModel(type='ENTITY', attributes=attributes)
        self.cache.store_node(resource=self.get_graph(),
                              token=ann_token, body=entity_node)

        # Then we add a relationship edge (of type ANNOTATED)
        annotates = pennprov.RelationModel(
            type='ANNOTATED', subject_id=node_token, object_id=ann_token, attributes=[])
        self.cache.store_relation(resource=self.get_graph(), body=annotates, label='_annotated')

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
        node_token = self.get_token_qname(self.get_entity_id(stream_name, stream_index - 1))

        ann_token = self.get_token_qname(self.get_entity_id(stream_name + '.' + annotation_name, stream_index - 1))

        # The key/value pair will itself be an entity node
        attributes = [
            pennprov.Attribute(name=self.get_token_qname(annotation_name), value=annotation_value,
                               type='STRING')]
        self._write_annot(ann_token, node_token, attributes)

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
            window_token = self.get_token_qname(self.get_window_id(output_stream_name, output_stream_index - 1))
        else:
            window_token = self.get_token_qname(self.get_window_id(output_stream_name, output_stream_index))

        # Finally, we build an entity node within the graph, with the token and the
        # attributes
        coll_node = pennprov.NodeModel(type='COLLECTION', attributes=[])
        self.cache.store_node(resource=self.get_graph(),
                              token=window_token, body=coll_node)

        logging.debug('Storing COLLECTION %s' % str(window_token))

        for token in input_tokens_list:
            # Add a relationship edge (of type ANNOTATED)
            # from window to its inputs
            token_qname = self.get_token_qname(token)
            annotates = pennprov.RelationModel(
                type='MEMBERSHIP', subject_id=window_token, object_id=token_qname, attributes=[])

            self.cache.store_relation(resource=self.get_graph(), body=annotates, label='hadMember')

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
        # type: (str, int, BasicTuple, list, str, int, int) -> pennprov.QualifiedName
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

        derives = pennprov.RelationModel(
            type='DERIVATION', subject_id=result_token, object_id=input_token, attributes=[])
        self.cache.store_relation(resource=self.get_graph(), body=derives, label='wasDerivedFrom')

        uses = pennprov.RelationModel(
            type='USAGE', subject_id=activity_token, object_id=input_token, attributes=[])
        self.cache.store_relation(resource=self.get_graph(), body=uses, label='used')

        generates = pennprov.RelationModel(
            type='GENERATION', subject_id=result_token, object_id=activity_token, attributes=[])
        self.cache.store_relation(resource=self.get_graph(), body=generates, label='wasGeneratedBy')

        return result_token

    def create_collection(self,
                          collection_name, collection_version=None,
                          prior_token=None):
        # type: (str, int, pennprov.QualifiedName) -> pennprov.QualifiedName
        """
        We can create a collection to represent a sub-sequence, a sub-stream, or a subset of items

        :param collection_name:
        :param collection_version:
        :param prior_token:
        :return:
        """
        token = self.get_token_qname(self.get_entity_id(collection_name, collection_version))

        data = []
        # data.append(pennprov.Attribute(name='collection', value=collection_name, type='STRING'))
        # if collection_version:
        #     data.append(pennprov.Attribute(name='version', value=collection_version, type='INTEGER'))

        # Create a node for the collection
        coll_node = pennprov.NodeModel(type='COLLECTION', attributes=data)
        self.cache.store_node(resource=self.get_graph(),
                              token=token, body=coll_node)

        if prior_token:
            derives = pennprov.RelationModel(
                type='REVISION', subject_id=token, object_id=prior_token, attributes=[])
            self.cache.store_relation(resource=self.get_graph(), body=derives, label='wasDerivedFrom')

        return token

    def add_to_collection(self, tuple_token, collection_token):
        # type (pennprov.QualifiedName, pennprov.QualifiedName) -> pennprov.QualifiedName
        """
        Associate a tuple with a collection (using the tokens for each)

        :param tuple_token:
        :param collection_token:
        :return:
        """
        part_of = pennprov.RelationModel(
            type='MEMBERSHIP', subject_id=collection_token, object_id=tuple_token, attributes=[])

        self.cache.store_relation(resource=self.get_graph(), body=part_of, label='hadMember')

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
        self.cache.store_relation(resource=self.get_graph(), body=derives, label='wasDerivedFrom')

        uses = pennprov.RelationModel(
            type='USAGE', subject_id=activity_token, object_id=window_token, attributes=[])
        self.cache.store_relation(resource=self.get_graph(), body=uses, label='used')

        generates = pennprov.RelationModel(
            type='GENERATION', subject_id=result_token, object_id=activity_token, attributes=[])
        self.cache.store_relation(resource=self.get_graph(), body=generates, label='wasGeneratedBy')

        return result_token

    def _get_qname(self, local_part):
        # types: (str) -> pennprov.QualifiedName
        """
        Returns a qualified name from a string to be used as the local part
        :param local_part:
        :return:
        """
        return pennprov.QualifiedName(self.namespace, local_part)

    def get_token_qname(self, token):
        # types: (str) -> pennprov.QualifiedName
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

    @classmethod
    def parse_qname(cls, token_value):
        # types (str) -> pennprov.QualifiedName
        """
        Returns a QualifiedName by parsing the given string as a namespace and local part
        :param token_value: a string of the form '{' + namespace + '}' + local_part
        :return: the corresponding pennprov.QualifiedName
        """
        match = cls.QNAME_REGEX.match(token_value)
        if not match:
            raise ValueError('cannot parse as QualfiedName:', token_value)
        qname = pennprov.QualifiedName(namespace=match.group(1), local_part=match.group(2))
        return qname

    def store_derived_from(self, derived_node, source_node):
        # types: (pennprov.QualifiedName, pennprov.QualifiedName) -> pennprov.QualifiedName
        """
        Stores a derivation of an output from an input
        :param derived_node:
        :param source_node:
        :return:
        """
        derives = pennprov.RelationModel(
            type='DERIVATION', subject_id=derived_node, object_id=source_node, attributes=[])
        self.cache.store_relation(resource=self.get_graph(), body=derives, label='wasDerivedFrom')

    def store_used(self, activity_node, input_node):
        # types: (pennprov.QualifiedName, pennprov.QualifiedName) -> pennprov.QualifiedName
        """
        Stores a usage relationship between an activity and an input
        :param activity_node:
        :param input_node:
        :return:
        """
        uses = pennprov.RelationModel(
            type='USAGE', subject_id=activity_node, object_id=input_node, attributes=[])
        self.cache.store_relation(resource=self.get_graph(), body=uses, label='used')

    def store_generated_by(self, output_node, activity_node):
        # types: (pennprov.QualifiedName, pennprov.QualifiedName) -> pennprov.QualifiedName
        """
        Stores an edge indicating an output was generated by an activity
        :param self:
        :param output_node:
        :param activity_node:
        :return:
        """
        generates = pennprov.RelationModel(
            type='GENERATION', subject_id=output_node, object_id=activity_node, attributes=[])
        self.cache.store_relation(resource=self.get_graph(), body=generates, label='wasGeneratedBy')

    def get_node(self, entity_id):
        # type: (pennprov.QualifiedName) -> List[Dict]
        """
        Returns the tuple data associated with a node ID (generally an entity node)
        :param entity_id:
        :return:
        """
        result = self.cache.get_provenance_data(self.get_graph(), (entity_id))

        return result

    def get_source_entities(self, entity_id):
        # type: (pennprov.QualifiedName) -> List[pennprov.QualifiedName]
        """
        Given an entity node, what was it derived from?
        :param entity_id:
        :return:
        :param entity_id:
        :return:
        """
        results = self.cache.get_connected_from(self.get_graph(), (entity_id), 'wasDerivedFrom')
        # results = [self.parse_qname(tok.token_value) for tok in results.tokens]
        return results

    def get_derived_entities(self, entity_id):
        # type: (pennprov.QualifiedName) -> List[pennprov.QualifiedName]
        results = self.cache.get_connected_to(self.get_graph(), (entity_id), 'wasDerivedFrom')
        # results = [self.parse_qname(tok.token_value) for tok in results.tokens]
        return results

    # def get_predecessor_entities(self, entity_id):
    #     # type: (pennprov.QualifiedName) -> List[pennprov.QualifiedName]
    #     return
    #
    # def get_successor_entities(self, entity_id):
    #     # type: (pennprov.QualifiedName) -> List[pennprov.QualifiedName]
    #     return

    def get_parent_entities(self, entity_id):
        # type: (pennprov.QualifiedName) -> List[pennprov.QualifiedName]
        """
        Find a parent collection (ie a node where this node is a member)
        :param entity_id:
        :return:
        """
        results = self.cache.get_connected_to(self.get_graph(), (entity_id), 'hadMember')
        # results = [self.parse_qname(tok.token_value) for tok in results.tokens]
        return results

    def get_child_entities(self, entity_id):
        # type: (pennprov.QualifiedName) -> List[pennprov.QualifiedName]
        """
        Find any child (member) nodes
        :param entity_id:
        :return:
        """
        results = self.cache.get_connected_from(self.get_graph(), (entity_id), 'hadMember')
        # results = [self.parse_qname(tok.token_value) for tok in results.tokens]
        return results

    def get_creating_activities(self, entity_id):
        # type: (pennprov.QualifiedName) -> List[pennprov.QualifiedName]
        """
        Get the list of activities that from which this output was generated
        :param entity_id:
        :return:
        """
        results = self.cache.get_connected_from(self.get_graph(), (entity_id), 'wasGeneratedBy')
        # results = [self.parse_qname(tok.token_value) for tok in results.tokens]
        return results

    def get_activity_outputs(self, activity_id):
        # type: (pennprov.QualifiedName) -> List[pennprov.QualifiedName]
        """
        Get the list of entities this activity generated
        :param activity_id:
        :return:
        """
        results = self.cache.get_connected_to(self.get_graph(), (activity_id), 'wasGeneratedBy')
        # results = [self.parse_qname(tok.token_value) for tok in results.tokens]
        return results

    def get_activity_inputs(self, activity_id):
        # type: (pennprov.QualifiedName) -> List[pennprov.QualifiedName]
        """
        Given an activity, what inputs did it use?
        :param activity_id:
        :return:
        """
        results = self.cache.get_connected_from(self.get_graph(), (activity_id), 'used')
        # results = [self.parse_qname(tok.token_value) for tok in results.tokens]
        return results

    def get_annotations(self, node_id):
        # type: (pennprov.QualifiedName) -> List[dict]
        """
        Given a node, find its annotations and return as a list of typed key/values
        :param node_id:
        :return:
        """
        results = self.cache.get_connected_from(self.get_graph(), (node_id), '_annotated')
        # results = [self.parse_qname(tok.token_value) for tok in results.tokens]

        results = [self.get_node(eid) for eid in results]

        return results

    # def get_entity_and_ancestor_annotations(self, entity_id):
    #     # type: (pennprov.QualifiedName) -> dict
    #     return

    def get_stream_inputs(self, stream_name):
        inputs = []

        stream_node = self.get_token_qname(self.get_entity_id(stream_name))

        for node in self.get_source_entities(stream_node):
            inputs.append(self.get_stream_from_entity_id(node.local_part))

        return inputs

    def get_stream_producers(self, stream_name):
        producers = []
        stream_node = self.get_token_qname(self.get_entity_id(stream_name))

        for node in self.get_creating_activities(stream_node):
            code = self.get_node(node)

            if len(code) > 0:
                code_id  = code[0]['hash']
                code = self.get_node(self.get_token_qname(code_id))
                producers.append(code[1]['code'])

        return producers

    def flush(self):
        return

    def close(self):
        return

    def __del__(self):
        self.close()
    