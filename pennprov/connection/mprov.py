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

from suffix_tree import Tree

import psycopg2
from psycopg2.extensions import cursor
from pennprov.config import config

class LogIndex:

    def add_node(self, db, resource, label, skolem_args):
        return 1

    def add_edge(self, db, resource, source, label, dest):
       return 1

    def add_nodeprop(self, db, resource, node, label, value, ind=None):
        return 1

# TO DO:
#  stream the update log
#  set epoch
#  build a suffix trie for the epoch
#  for each item
#    append to the string
#    replay suffixes up to max length
#    reuse extent at LCS
#    for each longer suffix, point to prior extent

class DirectWriteLogIndex(LogIndex):
    """
    Pass-through interface for provenance event logs
    """
    def add_node(self, db, resource, label, skolem_args):
        # type: (cursor, str, str, str) -> int
        """
        Inserts a node into the database cursor, for the given resource, with a given label.
        The skolem_args will be the basis of the value
        """
        logging.debug('Node: ' + label + '(' + skolem_args + ')')
        return db.execute("INSERT INTO MProv_Node(_key,_resource,label) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING RETURNING _created", \
            (skolem_args,resource,label))

    def add_nodeprop(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, Any, int) -> int
        logging.debug('NodeProp: ' + node + ' ' + label + ': ' + str(value))
        if isinstance(value, str):
            return self.add_nodeprop_str(db, resource, node, label, value, ind)
        elif isinstance(value, int):
            return self.add_nodeprop_int(db, resource, node, label, value, ind)
        elif isinstance(value, float):
            return self.add_nodeprop_float(db, resource, node, label, value, ind)
        elif isinstance(value, datetime.datetime):
            return self.add_nodeprop_date(db, resource, node, label, value, ind)
        else:
            raise Exception('Unknown type')


    def add_nodeprop_str(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, str, int) -> int
        if ind:
            return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,value,code,index) VALUES(%s,%s,%s,%s,'S',%s) ON CONFLICT DO NOTHING", \
                (node, resource, label, value, ind))
        else:
            return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,value,code) VALUES(%s,%s,%s,%s,'S') ON CONFLICT DO NOTHING", \
                (node, resource, label, value))

    def add_nodeprop_int(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, int, int) -> int
        if ind:
            return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,ivalue,code,index) VALUES(%s,%s,%s,%s,'I',s) ON CONFLICT DO NOTHING", \
                (node, resource, label, value, ind))
        else:
            return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,ivalue,code) VALUES(%s,%s,%s,%s,'I') ON CONFLICT DO NOTHING", \
                (node, resource, label, value))

    def add_nodeprop_float(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, float, int) -> int
        if ind:
            return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,fvalue,code,index) VALUES(%s,%s,%s,'F',%s) ON CONFLICT DO NOTHING", \
                (node, resource, label, value, ind))
        else:
            return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,fvalue,code) VALUES(%s,%s,%s,'F') ON CONFLICT DO NOTHING", \
                (node, resource, label, value))

    def add_nodeprop_date(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, datetime.datetime, int) -> int
        if ind:
            return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,tvalue,code,index) VALUES(%s,%s,%s,%s,'T',%s) ON CONFLICT DO NOTHING", \
                (node, resource, label, value, ind))
        else:
            return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,tvalue,code) VALUES(%s,%s,%s,'T') ON CONFLICT DO NOTHING", \
                (node, resource, label, value))

    def add_edge(self, db, resource, source, label, dest):
        # type: (cursor, str, str, str, str) -> int
        logging.debug('Edge: (' + source + ',' + label +',' + dest + ')')
        return db.execute("INSERT INTO MProv_Edge(_resource,_from,_to,label) VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING", \
            (resource, source, dest, label))

class CompressingLogIndex(LogIndex):
    # Basic format:
    # index -> (op_type, (tokens))
    #   op_type is one of: n(add_node), e(add_edge), p(add_prop), r(repeat), 2(seq_2), f(for), s(span)
    #   add_node(tok), add_edge(tok1,lab,tok2), add_prop(tok1,tok2,tok3), repeat(index), 2(index1,index2)
    #   f(p_index,index), s(start_p_index,stop_p_index,index)
    compression_table = [('n',(0))]
    # token: (index, tok, binding_p1, prior_binding), ...
    binding_table = []
    # p_index: pred
    pred_table = []

    # Inverse mapping from binding to index in binding table
    binding_to_index = {}

    # Log compression window
    recent_history = []

    op_history = []
    binding_history = []

    chain = {'last': []}

    tree = Tree ()

    real_index = DirectWriteLogIndex()
    last_node = None

    def add_node(self, db, resource, label, skolem_args):
        # type: (cursor, str, str, str) -> int
        ind = 0     # always use (n, 0)? TODO: expand to include repetition
        self.binding_to_index[skolem_args] = ind
        # TODO: push item to binding table
        #return len(self.binding_table) - 1
        self._add_log_event(('N',label),(skolem_args))
        return self.real_index.add_node(db, resource, label, skolem_args)

    def add_edge(self, db, resource, source, label, dest):
        # type: (cursor, str, str, str, str) -> int
        #return len(self.binding_table) - 1
        self._add_log_event(('E',label),(source,dest))
        return self.real_index.add_edge(db, resource, source, label, dest)

    def add_nodeprop(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, Any, int) -> int
        #return len(self.binding_table) - 1
        self._add_log_event(('P',label,ind),(node,value))
        return self.real_index.add_nodeprop(db, resource, node, label, value, ind)

    def _add_binding(self, log_id, binding_tuple):
        self.binding_history.append((log_id, binding_tuple))

    def _add_log_event(self, log_tuple, binding_tuple):
        self.op_history.append(log_tuple)

        found = False
        end = len(self.op_history)
        for i in range (0, end):
            if self.tree.find(self.op_history[end-i-1:]):
                found = True
                self.op_history = self.op_history[end-i-1:]
                break

        # TODO: find lcs
            
        if found:#self.tree.find(self.op_history):
            #found = True
            # Compression here, need to capture the last item
            for id,path in self.tree.find_all(self.op_history):
                last_node = id
                break
            #self.op_history = self.op_history[start]
            #logging.warning(str(self.op_history) + ' repeats ' + str(last_node) + '||' + str(self.chain['last']))
            self.chain['last'] = [last_node] + self.chain['last']
        else:
            # Flush
            if len(self.chain['last']):
                logging.warning('Flush sequence ' + str(self.chain['last']))
            last_node = len(self.binding_history)
            self.tree.add(len(self.binding_history), self.op_history)
            logging.warning(str(self.op_history) + ' assigned to ' + str(last_node))
            self.chain['last'] = []
            # TODO: Log an entry from binding to
        
        self._add_binding(last_node, binding_tuple)
        logging.debug(str(log_tuple) + ': ' + str(binding_tuple))

class MProvConnection:
    graph_name = None
    namespace = 'http://mprov.md2k.org'
    default_host = "localhost"
    QNAME_REGEX = re.compile('{([^}]*)}(.*)')

    #log = DirectWriteLogIndex()
    log = CompressingLogIndex()

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
                                                           tsvalue TIMESTAMP,
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
                                                           tsvalue TIMESTAMP,
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
        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM MProv_Edge WHERE _resource = (%s)", (self.get_graph(),))
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
        inputs = []

        stream_node = self.get_token_qname(self.get_entity_id(stream_name))

        for node in self.get_source_entities(stream_node):
            inputs.append(self.get_stream_from_entity_id(MProvConnection.get_local_part(node)))

        return inputs

    def get_stream_producers(self, stream_name):
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
        # types (str) -> str
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
        ret = []
        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT index,code,value,ivalue,lvalue,fvalue,dvalue,tvalue,tsvalue,label FROM MProv_NodeProp WHERE _resource = (%s) AND _key = (%s)", (resource,token))

                results = cursor.fetchall()
                ret = {}#[None for i in range(0,len(results))]
                for res in results:
                    #print(res)
                    inx = res[0]
                    if inx is None:
                        inx = res[9]
                    if res[1] is None or res[1] == 'S':
                        ret[inx] = res[2]
                    elif res[1] == 'I':
                        ret[inx] = res[3]
                    elif res[1] == 'L':
                        ret[inx] = res[4]
                    elif res[1] == 'F':
                        ret[inx] = res[5]
                    elif res[1] == 'D':
                        ret[inx] = res[6]
                    elif res[1] == 'T':
                        ret[inx] = res[7]
                    elif res[1] == 't':
                        ret[inx] = res[8]
                    else:
                        raise RuntimeError('Unknown code ' + res[1])


                #print ("Results:", token, cursor.fetchall())

        return [ret]

    def get_connected_to(self, resource, token, label1):
        # type: (str, str, str) -> List[pennprov.ProvTokenSetModel]
        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                if label1 is None:
                    cursor.execute("SELECT _from FROM MProv_Edge WHERE _resource = (%s) AND _to = (%s)", (resource,token))
                else:
                    cursor.execute("SELECT _from FROM MProv_Edge WHERE _resource = (%s) AND _to = (%s) AND label = (%s)",
                                   (self.get_graph(), token, label1))
                return [x[0] for x in cursor.fetchall()]
        return []

    def get_connected_from(self, resource, token, label1):
        # type: (str, str, str) -> List[pennprov.ProvTokenSetModel]
        with self.graph_conn as conn:
            with conn.cursor() as cursor:
                if label1 is None:
                    cursor.execute("SELECT _to FROM MProv_Edge WHERE _resource = (%s) AND _from = (%s)", (resource,token))
                else:
                    cursor.execute("SELECT _to FROM MProv_Edge WHERE _resource = (%s) AND _from = (%s) AND label = (%s)",
                                   (self.get_graph(), token, label1))
                return [x[0] for x in cursor.fetchall()]
        return []

    def flush(self):
        return

    def close(self):
        return

    def __del__(self):
        self.close()
    