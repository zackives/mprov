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

from typing import List, Any, Dict, Tuple
import logging
import pennprov
import datetime

import uuid
from uuid import UUID

from suffix_tree import Tree

from psycopg2.extensions import cursor
from psycopg2.extras import execute_values
import psycopg2.extras

class ProvenanceStore:
    """
    A persistent provenance graph storage subsystem.
    """

    def get_index():
        # type: () -> ProvenanceStore
        """
        Retrieve the appropriate provenance indexing subsystem
        """
        return EventBindingProvenanceStore()
        #return CachingSQLProvenanceStore()
        #return CompressingLogIndex(CachingLogIndex())

    def add_node(self, db, resource, label, skolem_args):
        # type: (cursor, str, str, str) -> None
        return 1

    def add_edge(self, db, resource, source, label, dest):
        # type: (cursor, str, str, str, str) -> None
       return 1

    def add_nodeprop(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, Any, int) -> None
        return 1

    def flush(self, db):
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
        # type: (cursor, str, str, str) -> List[pennprov.ProvTokenSetModel]
        return

    def get_connected_from(self, db, resource, token, label1):
        # type: (cursor, str, str, str) -> List[pennprov.ProvTokenSetModel]
        return

    def get_edges(self, db, resource):
        #type: (cursor, str) -> List[Tuple]
        return []

    def get_nodes(self, db, resource):
        #type: (cursor, str) -> List[Dict]
        return []

# TO DO:
#  stream the update log
#  set epoch
#  build a suffix trie for the epoch
#  for each item
#    append to the string
#    replay suffixes up to max length
#    reuse extent at LCS
#    for each longer suffix, point to prior extent

class SQLProvenanceStore(ProvenanceStore):
    """
    Writes the provenance graph to a PostgreSQL back-end.
    """

    def create_tables(self, cursor):
        # type: (cursor) -> None
        node_table = """
                     CREATE UNLOGGED TABLE IF NOT EXISTS MProv_Node(_key VARCHAR(80) NOT NULL,
                                                           _resource VARCHAR(80) NOT NULL,
                                                           _created SERIAL,
                                                           label VARCHAR(80),
                                                           PRIMARY KEY(_resource, _key))
                     """

        node_props_table = """
                     CREATE UNLOGGED TABLE IF NOT EXISTS MProv_NodeProp(_key VARCHAR(80) NOT NULL,
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
                                                           UNIQUE(_resource,_key,index)
                                                           )
                           """

        edge_table = """
                     CREATE UNLOGGED TABLE IF NOT EXISTS MProv_Edge(_key SERIAL,
                                                           _resource VARCHAR(80) NOT NULL,
                                                           _from VARCHAR(80) NOT NULL,
                                                           _to VARCHAR(80) NOT NULL,
                                                           label VARCHAR(80),
                                                           PRIMARY KEY(_resource, _key),
                                                           UNIQUE(_resource, _from, _to, label)
                                                           )
                     """

        edge_props_table = """
                     CREATE UNLOGGED TABLE IF NOT EXISTS MProv_EdgeProp(_key INTEGER NOT NULL,
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
                                                           UNIQUE(_resource,_key,index)
                                                           )
                           """

        schema_table = """
                     CREATE UNLOGGED TABLE IF NOT EXISTS MProv_Schema(_key VARCHAR(80) NOT NULL,
                                                           _resource VARCHAR(80) NOT NULL,
                                                           name VARCHAR(80) NOT NULL,
                                                           value VARCHAR,
                                                           PRIMARY KEY(_resource, _key),
                                                           UNIQUE(_resource, name)
                                                           )
                       """

        cursor.execute(node_table)
        cursor.execute(node_props_table)
        cursor.execute(edge_table)
        cursor.execute(edge_props_table)
        cursor.execute(schema_table)

    def clear_tables(self, cursor, graph):
        # type: (cursor, str) -> None
        cursor.execute("DELETE FROM MProv_Edge WHERE _resource = (%s)", (graph,))
        cursor.execute("DELETE FROM MProv_Node WHERE _resource = (%s)", (graph,))
        cursor.execute("DELETE FROM MProv_NodeProp WHERE _resource = (%s)", (graph,))

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

    def get_provenance_data(self, db, resource, token):
        # type: (cursor, str, str) -> List[Dict]
        self.flush(db)
        ret = []
        db.execute("SELECT index,code,value,ivalue,lvalue,fvalue,dvalue,tvalue,tsvalue,label FROM MProv_NodeProp WHERE _resource = (%s) AND _key = (%s)", (resource,token))

        results = db.fetchall()
        ret = {}
        for res in results:
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

        return [ret]

    def get_connected_to(self, db, resource, token, label1):
        # type: (cursor, str, str, str) -> List[pennprov.ProvTokenSetModel]
        self.flush(db)
        if label1 is None:
            db.execute("SELECT _from FROM MProv_Edge WHERE _resource = (%s) AND _to = (%s)", (resource,token))
        else:
            db.execute("SELECT _from FROM MProv_Edge WHERE _resource = (%s) AND _to = (%s) AND label = (%s)",
                            (resource, token, label1))
        return [x[0] for x in db.fetchall()]

    def get_connected_from(self, db, resource, token, label1):
        # type: (cursor, str, str, str) -> List[pennprov.ProvTokenSetModel]
        self.flush(db)
        if label1 is None:
            db.execute("SELECT _to FROM MProv_Edge WHERE _resource = (%s) AND _from = (%s)", (resource,token))
        else:
            db.execute("SELECT _to FROM MProv_Edge WHERE _resource = (%s) AND _from = (%s) AND label = (%s)",
                            (resource, token, label1))
        return [x[0] for x in db.fetchall()]

    def get_edges(self, db, resource):
        #type: (cursor, str) -> List[Tuple]
        self.flush(db)
        db.execute("SELECT _from,label,_to FROM MProv_Edge WHERE _resource = (%s)", (resource,))

        return [(x[0],x[1],x[2]) for x in db.fetchall()]

    def get_nodes(self, db, resource):
        #type: (cursor, str) -> List[Dict]
        self.flush(db)
        ret_list = []

        # Get the nodes first
        db.execute("""SELECT n.label,n._key 
            FROM MProv_Node n WHERE n._resource=%s""", 
            (resource,))
        results = db.fetchall()
        for res in results:
            ret = {}
            ret['id'] = res[1]
            ret['label'] = res[0]
            ret_list = ret_list + [ret]

        for ret in ret_list:
            db.execute("""SELECT index,code,value,ivalue,lvalue,fvalue,dvalue,tvalue,tsvalue,label
                FROM MProv_NodeProp WHERE _key = %s AND _resource = (%s)""", 
                (ret['id'], resource,))

            # db.execute("""SELECT index,code,value,ivalue,lvalue,fvalue,dvalue,tvalue,tsvalue,n.label,np.label,np._key 
            #     FROM MProv_Node n LEFT JOIN MProv_NodeProp np ON np._key = n._key WHERE np._resource = (%s)""", 
            #     (resource,))

            results = db.fetchall()
            for res in results:
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

                logging.info("Node: " + str(ret))

        return ret_list


    def flush(self, db):
        # type: (cursor) -> None
        return


class EventBindingProvenanceStore(ProvenanceStore):

    event_queue = []
    binding_queue = []
    total = 0

    def create_tables(self, cursor):
        # type: (cursor) -> None
        # node_table = """
        #              CREATE UNLOGGED TABLE IF NOT EXISTS MProv_Node(_key VARCHAR(80) NOT NULL,
        #                                                    _resource VARCHAR(80) NOT NULL,
        #                                                    _created SERIAL,
        #                                                    label VARCHAR(80),
        #                                                    PRIMARY KEY(_resource, _key))
        #              """

        event_table = """
                    CREATE UNLOGGED TABLE IF NOT EXISTS MProv_Event(_key UUID PRIMARY KEY,
                                                            _resource VARCHAR(80) NOT NULL,
                                                            code CHAR(1),
                                                            label VARCHAR(80),
                                                            args VARCHAR)
        """

        binding_table = """
                    CREATE UNLOGGED TABLE IF NOT EXISTS MProv_Binding(event UUID NOT NULL,
                                                            index INTEGER,
                                                            code CHAR(1),
                                                            svalue VARCHAR,
                                                            ivalue INTEGER,
                                                            lvalue BIGINT,
                                                            dvalue DOUBLE PRECISION,
                                                            fvalue REAL,
                                                            tvalue DATE,
                                                            tsvalue TIMESTAMP,
                                                            uvalue UUID,
                                                            svalue2 VARCHAR,
                                                            UNIQUE (uvalue,index))
        """

        #,                                                            UNIQUE (event,_resource,index,svalue)

        # node_props_table = """
        #              CREATE UNLOGGED TABLE IF NOT EXISTS MProv_NodeProp(_key VARCHAR(80) NOT NULL,
        #                                                    _resource VARCHAR(80) NOT NULL,
        #                                                    type VARCHAR(80),
        #                                                    label VARCHAR(80),
        #                                                    value VARCHAR,
        #                                                    code CHAR(1),
        #                                                    ivalue INTEGER,
        #                                                    lvalue BIGINT,
        #                                                    dvalue DOUBLE PRECISION,
        #                                                    fvalue REAL,
        #                                                    tvalue DATE,
        #                                                    tsvalue TIMESTAMP,
        #                                                    index BIGINT,
        #                                                    PRIMARY KEY(_resource, _key, label),
        #                                                    UNIQUE(_resource,_key,index)
        #                                                    )
        #                    """

        # edge_table = """
        #              CREATE UNLOGGED TABLE IF NOT EXISTS MProv_Edge(_key SERIAL,
        #                                                    _resource VARCHAR(80) NOT NULL,
        #                                                    _from VARCHAR(80) NOT NULL,
        #                                                    _to VARCHAR(80) NOT NULL,
        #                                                    label VARCHAR(80),
        #                                                    PRIMARY KEY(_resource, _key),
        #                                                    UNIQUE(_resource, _from, _to, label)
        #                                                    )
        #              """

        # edge_props_table = """
        #              CREATE UNLOGGED TABLE IF NOT EXISTS MProv_EdgeProp(_key INTEGER NOT NULL,
        #                                                    _resource VARCHAR(80) NOT NULL,
        #                                                    _created SERIAL,
        #                                                    type VARCHAR(80),
        #                                                    label VARCHAR(80),
        #                                                    value VARCHAR,
        #                                                    code CHAR(1),
        #                                                    ivalue INTEGER,
        #                                                    lvalue BIGINT,
        #                                                    dvalue DOUBLE PRECISION,
        #                                                    fvalue REAL,
        #                                                    tvalue DATE,
        #                                                    tsvalue TIMESTAMP,
        #                                                    index BIGINT,
        #                                                    PRIMARY KEY(_resource, _key, label),
        #                                                    UNIQUE(_resource,_key,index)
        #                                                    )
        #                    """

        schema_table = """
                     CREATE UNLOGGED TABLE IF NOT EXISTS MProv_Schema(_key VARCHAR(80) NOT NULL,
                                                           _resource VARCHAR(80) NOT NULL,
                                                           name VARCHAR(80) NOT NULL,
                                                           value VARCHAR,
                                                           PRIMARY KEY(_resource, _key),
                                                           UNIQUE(_resource, name)
                                                           )
                       """

        # cursor.execute(node_table)
        cursor.execute(event_table)
        cursor.execute(binding_table)
        # cursor.execute(node_props_table)
        # cursor.execute(edge_table)
        # cursor.execute(edge_props_table)
        cursor.execute(schema_table)
        psycopg2.extras.register_uuid()

    def clear_tables(self, cursor, graph):
        # type: (cursor, str) -> None
        # cursor.execute("DELETE FROM MProv_Node WHERE _resource = (%s)", (graph,))
        # cursor.execute("DELETE FROM MProv_Edge WHERE _resource = (%s)", (graph,))
        # cursor.execute("DELETE FROM MProv_NodeProp WHERE _resource = (%s)", (graph,))
        cursor.execute("DELETE FROM MProv_Binding", (graph, ))
        cursor.execute("DELETE FROM MProv_Event WHERE _resource = (%s)", (graph, ))


    def _add_node_binding(self, id, label, resource, args):
        #self.binding_queue.append((id,resource,None,None,args,None,None,None,None,None,None))
        self.binding_queue.append((id,None,None,args,None,None,None,None,None,None,None,None))

    def _add_edge_binding(self, id, resource, source, label, dest):
        uuid = self._get_id_from_key(source + '\\' + label + '\\' + dest)
        self.binding_queue.append((id,None,None,source,None,None,None,None,None,None,uuid,dest))
        #self.binding_queue.append((id,0,None,source,None,None,None,None,None,None,uuid))
        #self.binding_queue.append((id,1,None,dest,None,None,None,None,None,None,uuid))
        return


    def _add_node_property_str_binding(self, resource, id, node, label,  value, ind):
        uuid = self._get_id_from_key(node + '\\' + label)
        self.binding_queue.append((id,ind,None,value,None,None,None,None,None,None,uuid,None))
        return

    def _add_node_property_int_binding(self, resource, id, node, label,  value, ind):
        uuid = self._get_id_from_key(node + '\\' + label)
        self.binding_queue.append((id,ind,None,None,value,None,None,None,None,None,uuid,None))
        return

    def _add_node_property_float_binding(self, resource, id, node, label,  value, ind):
        uuid = self._get_id_from_key(node + '\\' + label)
        self.binding_queue.append((id,ind,None,None,None,None,value,None,None,None,uuid,None))
        return

    def _add_node_property_datetime_binding(self, resource, id, node, label,  value, ind):
        uuid = self._get_id_from_key(node + '\\' + label)
        self.binding_queue.append((id,ind,None,None,None,None,None,None,None,value,uuid,None))
        return

    """
    Pass-through interface for provenance event logs
    """
    def add_node(self, db, resource, label, node_identifier):
        # type: (cursor, str, str, str) -> int
        """
        Inserts a node into the database cursor, for the given resource, with a given label.
        The skolem_args will be the basis of the value
        """

        # We are going to create a unique node signature including the node
        #logging.debug('Node: ' + label + '(' + skolem_args + ')')

        logging.info('Adding node %s:%s' %(label,node_identifier))
        id = self._add_node_event(db, resource, label, node_identifier)
        self._add_node_binding(id, label, resource, node_identifier)

        #return db.execute("INSERT INTO MProv_Node(_key,_resource,label) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING RETURNING _created", \
        #    (node_identifier,resource,label))
        return 1

    def add_nodeprop(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, Any, int) -> int
        id = self._add_node_property_event(db, resource, label, value)
        logging.debug('NodeProp: ' + node + ' ' + label + ': ' + str(value))
        if isinstance(value, str):
            return self._add_node_property_str_binding(resource, id, node, label,  value, ind)
            #return self.add_nodeprop_str(db, resource, node, label, value, ind)
        elif isinstance(value, int):
            return self._add_node_property_int_binding(resource, id, node, label,  value, ind)
            #return self.add_nodeprop_int(db, resource, node, label, value, ind)
        elif isinstance(value, float):
            return self._add_node_property_float_binding(resource, id, node, label,  value, ind)
            #return self.add_nodeprop_float(db, resource, node, label, value, ind)
        elif isinstance(value, datetime.datetime):
            return self._add_node_property_datetime_binding(resource, id, node, label,  value, ind)
            #return self.add_nodeprop_date(db, resource, node, label, value, ind)
        else:
            raise Exception('Unknown type')


    # def add_nodeprop_str(self, db, resource, node, label, value, ind=None):
    #     # type: (cursor, str, str, str, str, int) -> int
    #     if ind:
    #         return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,value,code,index) VALUES(%s,%s,%s,%s,'S',%s) ON CONFLICT DO NOTHING", \
    #             (node, resource, label, value, ind))
    #     else:
    #         return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,value,code) VALUES(%s,%s,%s,%s,'S') ON CONFLICT DO NOTHING", \
    #             (node, resource, label, value))

    # def add_nodeprop_int(self, db, resource, node, label, value, ind=None):
    #     # type: (cursor, str, str, str, int, int) -> int
    #     if ind:
    #         return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,ivalue,code,index) VALUES(%s,%s,%s,%s,'I',s) ON CONFLICT DO NOTHING", \
    #             (node, resource, label, value, ind))
    #     else:
    #         return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,ivalue,code) VALUES(%s,%s,%s,%s,'I') ON CONFLICT DO NOTHING", \
    #             (node, resource, label, value))

    # def add_nodeprop_float(self, db, resource, node, label, value, ind=None):
    #     # type: (cursor, str, str, str, float, int) -> int
    #     if ind:
    #         return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,fvalue,code,index) VALUES(%s,%s,%s,'F',%s) ON CONFLICT DO NOTHING", \
    #             (node, resource, label, value, ind))
    #     else:
    #         return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,fvalue,code) VALUES(%s,%s,%s,'F') ON CONFLICT DO NOTHING", \
    #             (node, resource, label, value))

    # def add_nodeprop_date(self, db, resource, node, label, value, ind=None):
    #     # type: (cursor, str, str, str, datetime.datetime, int) -> int
    #     if ind:
    #         return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,tvalue,code,index) VALUES(%s,%s,%s,%s,'T',%s) ON CONFLICT DO NOTHING", \
    #             (node, resource, label, value, ind))
    #     else:
    #         return db.execute("INSERT INTO MProv_NodeProp(_key,_resource,label,tvalue,code) VALUES(%s,%s,%s,'T') ON CONFLICT DO NOTHING", \
    #             (node, resource, label, value))

    edge_count = 0
    def add_edge(self, db, resource, source, label, dest):
        # type: (cursor, str, str, str, str) -> int
        self.edge_count += 1
        logging.info('Adding edge %s: (%s, %s, %s)' %(self.edge_count, source, label, dest))
        id = self._add_edge_event(db, resource, label, None)
        self._add_edge_binding(id, resource, source, label, dest)
        #return db.execute("INSERT INTO MProv_Edge(_resource,_from,_to,label) VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING", \
        #    (resource, source, dest, label))
        return 1

    def get_provenance_data(self, db, resource, token):
        # type: (cursor, str, str) -> List[Dict]
        self.flush(db)
        ret = []
        db.execute("""SELECT b.index,b.code,b.svalue,b.ivalue,b.lvalue,b.fvalue,b.dvalue,b.tvalue,b.tsvalue,b.uvalue,e.label 
                      FROM MProv_Binding s 
                        JOIN MProv_Event e ON s.event = e._key
                        LEFT JOIN MProv_Binding b ON e._key = b.event
                      WHERE e._resource = (%s) AND (e.code = 'N' or e.code = 'P') AND s.index = NULL AND 
                        s.svalue = %s""", 
            (resource,token))

        results = db.fetchall()
        ret = {}
        for res in results:
            inx = res[0]
            if inx is None:
                inx = res[10]
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
            elif res[1] == 'u':
                ret[inx] = res[9]
            else:
                raise RuntimeError('Unknown code ' + res[1])

        return [ret]

    def _get_connected(self, db, resource, token, inx, label1):
        # type: (cursor, str, str, int, str) -> List[pennprov.ProvTokenSetModel]
        self.flush(db)
        if label1 is None:
            # Need to start with the DEST, which is index 1
            db.execute("""SELECT b.index,b.svalue,e.label 
                        FROM MProv_Binding s 
                            JOIN MProv_Event e ON s.event = e._key
                            LEFT JOIN MProv_Binding b ON e._key = b.event
                        WHERE e._resource = (%s) AND e.code = 'E' AND s.index = %s AND 
                            s.svalue = %s AND b.index <> s.index AND b.uvalue = s.uvalue""", 
                (resource,inx,token))
        else:
        # Need to start with the DEST, which is index 1
            db.execute("""SELECT b.index,b.svalue,e.label 
                        FROM MProv_Binding s 
                            JOIN MProv_Event e ON s.event = e._key
                            LEFT JOIN MProv_Binding b ON e._key = b.event
                        WHERE e._resource = (%s) AND e.code = 'E' AND s.index = %s AND 
                            s.svalue = %s AND e.label=%s AND b.index <> s.index AND s.uvalue = b.uvalue""", 
                (resource,inx,token,label1))

        return [x[1] for x in db.fetchall()]


    def get_connected_to(self, db, resource, token, label1):
        # type: (cursor, str, str, int, str) -> List[pennprov.ProvTokenSetModel]
        self.flush(db)
        if label1 is None:
            # Need to start with the DEST
            db.execute("""SELECT s.index,s.svalue,e.label 
                        FROM MProv_Binding s 
                            JOIN MProv_Event e ON s.event = e._key
                        WHERE e._resource = (%s) AND e.code = 'E' AND s.svalue2 = %s""", 
                (resource,token))
        else:
        # Need to start with the DEST
            db.execute("""SELECT s.index,s.svalue,e.label 
                        FROM MProv_Binding s 
                            JOIN MProv_Event e ON s.event = e._key
                        WHERE e._resource = (%s) AND e.code = 'E' AND 
                            s.svalue2 = %s AND e.label=%s""", 
                (resource,token,label1))

        return [x[1] for x in db.fetchall()]

    def get_connected_from(self, db, resource, token, label1):
        # type: (cursor, str, str, int, str) -> List[pennprov.ProvTokenSetModel]
        self.flush(db)
        if label1 is None:
            # Need to start with the SOURCE
            db.execute("""SELECT s.index,s.svalue2,e.label 
                        FROM MProv_Binding s 
                            JOIN MProv_Event e ON s.event = e._key
                        WHERE e._resource = (%s) AND e.code = 'E' AND 
                            s.svalue = %s""", 
                (resource,token))
        else:
        # Need to start with the SOURCE
            db.execute("""SELECT s.index,s.svalue2,e.label 
                        FROM MProv_Binding s 
                            JOIN MProv_Event e ON s.event = e._key
                        WHERE e._resource = (%s) AND e.code = 'E' AND 
                            s.svalue = %s AND e.label=%s""", 
                (resource,token,label1))

        return [x[1] for x in db.fetchall()]

    def _write_events(self, db):
        # type: (cursor) -> None
        if len(self.event_queue) > 0:
            execute_values(db,"INSERT INTO MProv_Event(_key,_resource,code,label,args) VALUES %s ON CONFLICT DO NOTHING", \
                self.event_queue)

        self.total += len(self.event_queue)
        self.event_queue.clear()
        return 1

    def _write_bindings(self, db):
        # type: (cursor) -> None
        if len(self.binding_queue) > 0:
            execute_values(db,"INSERT INTO MProv_Binding(event,index,code,svalue,ivalue,lvalue,dvalue,fvalue,tvalue,tsvalue,uvalue,svalue2) VALUES %s ON CONFLICT DO NOTHING", \
                self.binding_queue)

        self.total += len(self.binding_queue)
        self.binding_queue.clear()
        return 1

    def get_edges(self, db, resource):
        #type: (cursor, str) -> List[Tuple]
        self.flush(db)
        #db.execute("SELECT _from,label,_to FROM MProv_Edge WHERE _resource = (%s)", (resource,))
        db.execute("""SELECT s.svalue,e.label,s.svalue2
                    FROM MProv_Binding s 
                        JOIN MProv_Event e ON s.event = e._key
                    WHERE e._resource = (%s) AND e.code = 'E'""", 
            (resource,))

        return [(x[0],x[1],x[2]) for x in db.fetchall()]

    def get_nodes(self, db, resource):
        #type: (cursor, str) -> List[Dict]
        self.flush(db)
        ret_list = []
        db.execute("""SELECT e.label,s.svalue,s.event
                      FROM MProv_Binding s 
                        JOIN MProv_Event e ON s.event = e._key
                      WHERE e._resource = (%s) AND e.code = 'N'""", 
            (resource,))
        # db.execute("""SELECT index,code,value,ivalue,lvalue,fvalue,dvalue,tvalue,tsvalue,n.label,np.label,np._key 
        #     FROM MProv_Node n LEFT JOIN MProv_NodeProp np ON np._key = n._key WHERE np._resource = (%s)""", 
        #     (resource,))
        ret = {}

        results = db.fetchall()
        for res in results:
            ret = {}
            ret['id'] = res[1]
            ret['_event'] = res[2]
            ret['label'] = res[0]
            ret_list = ret_list + [ret]

        for ret in ret_list:
            db.execute("""SELECT s.index,s.svalue,s.ivalue,s.lvalue,s.dvalue,s.fvalue,s.tvalue,s.tsvalue,e.label
                        FROM MProv_Binding s 
                            JOIN MProv_Event e ON s.event = e._key
                            LEFT JOIN MProv_Binding b ON e._key = b.event
                        WHERE e._resource = (%s) AND e.code = 'P' AND s.uvalue=%s""", 
                (resource,ret['_event']))
            results = db.fetchall()
            for res in results:
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

        return ret_list

    def flush(self, db):
        # type: (cursor) -> None
        self._write_events(db)
        self._write_bindings(db)
        return

    def _get_id(self):
        # type: () -> UUID
        return uuid.uuid4()

    def _get_id_from_key(self, key):
        # type: (str) -> UUID
        return uuid.uuid5(uuid.NAMESPACE_URL, key)

    def _add_node_event(self, db, resource, label, args, id=None):
        # type: (cursor, str, str, str, UUID) -> UUID
        if id == None:
            id = self._get_id_from_key(resource + ':' + label + '\\N')# + str(args))

        self.event_queue.append((id, resource, 'N', label, None))#args))
        return id

    def _add_edge_event(self, db, resource, label, args, id=None):
        # type: (cursor, str, str, str, UUID) -> UUID
        if id == None:
            id = self._get_id_from_key(resource + ':' + label + '\\E')# + '\\N' + str(args))
        self.event_queue.append((id, resource, 'E', label, args))
        return id

    def _add_node_property_event(self, db, resource, label, args, id=None):
        # type: (cursor, str, str, str, UUID) -> UUID
        if id == None:
            id = self._get_id_from_key(resource + ':' + label + '\\P')# + '\\N' + str(args))
        self.event_queue.append((id, resource, 'P', label, None))#args))
        return id

class CachingSQLProvenanceStore(SQLProvenanceStore):
    MAX_ELEMENTS = 16384
    done = set()
    nodeprop_pool = set()
    node_pool = set()
    edge_pool = set()

    total = 0

    def flush(self, db):
        # type: (cursor) -> None
        if len(self.node_pool) > 0:
            print('Flushing nodes...')
            self._write_nodes(db)
        if len(self.edge_pool) > 0:
            print('Flushing edges...')
            self._write_edges(db)
        if len(self.nodeprop_pool) > 0:
            print('Flushing node properties...')
            self._write_nodeprops(db)
        print ('Total flushed: %d'%self.total)

    def _write_nodes(self, db):
        # type: (cursor) -> None
        execute_values(db,"INSERT INTO MProv_Node(_key,_resource,label) VALUES %s ON CONFLICT DO NOTHING", \
            self.node_pool)

        self.total += len(self.node_pool)
        self.node_pool.clear()
        return 1

    def _write_edges(self, db):
        # type: (cursor) -> None
        execute_values(db,"INSERT INTO MProv_Edge(_resource,_from,_to,label) VALUES %s ON CONFLICT DO NOTHING", \
            self.edge_pool)
        self.total += len(self.edge_pool)
        self.edge_pool.clear()
        return

    def _write_nodeprops(self, db):
        # type: (cursor) -> None
        execute_values(db,"INSERT INTO MProv_NodeProp(_key,_resource,type,label,value,code,ivalue,lvalue,dvalue,fvalue,tvalue,tsvalue,index) VALUES %s ON CONFLICT DO NOTHING", \
            self.nodeprop_pool)
        self.total += len(self.nodeprop_pool)
        self.nodeprop_pool.clear()
        return

    def add_node(self, db, resource, label, skolem_args):
        # type: (cursor, str, str, str) -> int
        """
        Inserts a node into the database cursor, for the given resource, with a given label.
        The skolem_args will be the basis of the value
        """
        logging.debug('Node: ' + label + '(' + skolem_args + ')')
        ins_str = (skolem_args,resource,label)
        self.node_pool.add(ins_str)
        if len(self.node_pool) > self.MAX_ELEMENTS:
            self._write_nodes(db)

    def add_nodeprop_str(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, str, int) -> int
        ins_str = (node,resource,None,label,value,'S',None,None,None,None,None, None, ind)

        self.nodeprop_pool.add(ins_str)
        if len(self.nodeprop_pool) > self.MAX_ELEMENTS:
            self._write_nodeprops(db)

    def add_nodeprop_int(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, int, int) -> int
        ins_str = (node,resource,None,label,None,'I',value,None,None,None,None, None, ind)
        self.nodeprop_pool.add(ins_str)
        if len(self.nodeprop_pool) > self.MAX_ELEMENTS:
            self._write_nodeprops(db)

    def add_nodeprop_float(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, float, int) -> int
        ins_str = (node,resource,None,label,None,'F',None,None,None,value,None, None, ind)
        #if ins_str not in self.done:
        self.nodeprop_pool.add(ins_str)
        #    self.done.add(ins_str)
        if len(self.nodeprop_pool) > self.MAX_ELEMENTS:
            self._write_nodeprops(db)

    def add_nodeprop_date(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, datetime.datetime, int) -> int
        ins_str = (node,resource,None,label,None,'T',None,None,None,None,value, None, ind)
        #if ins_str not in self.done:
        self.nodeprop_pool.add(ins_str)
        #    self.done.add(ins_str)
        if len(self.nodeprop_pool) > self.MAX_ELEMENTS:
            self._write_nodeprops(db)

    def add_edge(self, db, resource, source, label, dest):
        # type: (cursor, str, str, str, str) -> int
        logging.debug('Edge: (' + source + ',' + label +',' + dest + ')')
        ins_str = (resource, source, dest, label)
        self.edge_pool.add(ins_str)
        if len(self.edge_pool) > self.MAX_ELEMENTS:
            self._write_edges(db)

    def get_edges(self, db: cursor, resource: str) -> List[Tuple]:
        return super().get_edges(db, resource)

    def get_nodes(self, db: cursor, resource: str) -> List[Dict]:
        return super().get_nodes(db, resource)

class CompressingProvenanceStore(ProvenanceStore):
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

    real_index = None
    last_node = None

    def __init__(self, r_index):
        # type: (ProvenanceStore) -> None
        self.real_index = r_index

    def create_tables(self, db):
        # type: (cursor) -> None
        self.real_index.create_tables(db)

    def clear_tables(self, db, graph):
        # type: (cursor, str) -> None
        self.real_index.clear_tables(db, graph)

    def add_node(self, db, resource, label, skolem_args):
        # type: (cursor, str, str, str) -> int
        ind = 0     # always use (n, 0)? TODO: expand to include repetition
        self.binding_to_index[skolem_args] = ind
        # TODO: push item to binding table
        #return len(self.binding_table) - 1
        self._add_log_event(('N',label),(skolem_args),db)
        return self.real_index.add_node(db, resource, label, skolem_args)

    def add_edge(self, db, resource, source, label, dest):
        # type: (cursor, str, str, str, str) -> int
        #return len(self.binding_table) - 1
        self._add_log_event(('E',label),(source,dest),db)
        return self.real_index.add_edge(db, resource, source, label, dest)

    def add_nodeprop(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, Any, int) -> int
        #return len(self.binding_table) - 1
        self._add_log_event(('P',label,ind),(node,value),db)
        return self.real_index.add_nodeprop(db, resource, node, label, value, ind)

    def _add_binding(self, log_id, binding_tuple):
        self.binding_history.append((log_id, binding_tuple))

    def _add_log_event(self, log_tuple, binding_tuple,db):
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
            self.flush(db)
        
        self._add_binding(last_node, binding_tuple)
        logging.debug(str(log_tuple) + ': ' + str(binding_tuple))

    def flush(self, db):
        # type: (cursor) -> None
        self.real_index.flush(db)

    def get_provenance_data(self, db, resource, token):
        # type: (cursor, str, str) -> List[Dict]
        return self.real_index.get_provenance_data(db, resource, token)

    def get_connected_to(self, db, resource, token, label1):
        # type: (cursor, str, str, str) -> List[pennprov.ProvTokenSetModel]
        return self.real_index.get_connected_from(db, resource, token, label1)

    def get_connected_from(self, db, resource, token, label1):
        # type: (cursor, str, str, str) -> List[pennprov.ProvTokenSetModel]
        return self.real_index.get_connected_to(db, resource, token, label1)

    def get_nodes(self, db: cursor, resource: str) -> List[Dict]:
        return self.real_index.get_nodes(db, resource)

    def get_edges(self, db: cursor, resource: str) -> List[Tuple]:
        return self.real_index.get_edges(db, resource)