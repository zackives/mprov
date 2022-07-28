######################
## mProv Copyright (C) 2017-22 by Trustees of the University of Pennsylvania
## All Rights Reserved.
## 
##
# ## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
######################

from typing import List, Mapping, Any, Tuple
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DML, Text, Token, Wildcard

from pennprov.queries.parse_sql import extract_tables,is_subselect
from pennprov.sql.schema_registry import SchemaRegistry
from pennprov.metadata.dataframe_schema import Key

import sqlparse
import logging


class ProvenanceManager:
    registry = SchemaRegistry()

    def get_schema_registry(self):
        """
        The metadata management
        """
        return ProvenanceManager.registry


class SqlProvenanceManager(ProvenanceManager):
    def __init__(self):
        ProvenanceManager.__init__(self)

    def _create_provenance_tables(self, table_map: Mapping[str, str], sql: str) -> Mapping[str, str]:
        """
        """
        ret = {}
        for table in table_map:
            if table not in SchemaRegistry.created_tables:
                sql1 = 'CREATE TABLE ' + table + "_tab LIKE " + table + '_uid ' + self._table_storage()
                sql2 = table_map[table]

                #ret.append(sql2)
                #ret.append(sql1)
                ret[table + '_tab'] = sql1
                ret[table + '_uid'] = sql2
                SchemaRegistry.created_tables.add(table)
        return ret

    def _table_storage(self):
        return ''

    def _list_agg(self, items: str):
        return 'array_agg(' + items + ')'

    def _const_agg(self, items: str):
        select_str = ', '.join(items)
        return 'array(' + select_str + ')'

    def _rewrite_sql_statement(self, sql: str, table_map, select_items, has_groupby) -> str:
        """
        Goes through the SQL and updates the tables in the FROM clause to have appropriate
        provenance tables; and adds any select_items necessary to trace provenance through
        the query block

        sql: original SQL statement
        table_map: mapping from "raw" tables to provenance tables
        select_items: provenance columns that need to be added to the select statement
        """
        sql2 = ""

        # print ("Rewriting %s with %s and %s"%(sql, table_map, select_items))

        for statement in sqlparse.parse(sql):
            if not isinstance(statement, Statement):
                raise RuntimeError('Cannot get PROV query from something other than a select statement')

            select_seen = False
            from_seen = False
            skip_token = False
            for item in statement.tokens:
                if item.ttype is Text.Whitespace:
                    sql2 = sql2 + str(item)
                    continue
                
                if item.is_group and item[0].ttype is Keyword and item[0].value.upper() == 'WHERE':
                    # print ('WHERE %s' %item.tokens[1:])
                    sql2 = sql2 + str(item[0]).upper()
                    for item2 in item.tokens[1:]:
                        sql2 = sql2 + str(item2)
                    from_seen = False
                    select_seen = False
                elif item.ttype is not Keyword and item.ttype is not DML:
                    if from_seen:
                        if skip_token:
                            skip_Token = False
                            sql2 = sql2 + str(item)
                            continue
                        if is_subselect(item):
                            raise RuntimeError('Nested SELECTS should not be used. Instead break out the subquery and give it a name')
                        else:
                            rewrite = ''
                            if item.is_group:
                                table = str(item.tokens[0])
                                if table in table_map:
                                    table = table + '_tab'
                                    rewrite = str(table) 

                                    if len(item.tokens) == 1:
                                        rewrite = rewrite + ' as ' + str(item.tokens[0])
                                    else:
                                        for table in item.tokens[1:]:
                                            rewrite = rewrite + self.prune(str(table))
                                else:
                                    rewrite = str(item)
                            else:
                                table = str(item)
                                if table in table_map:
                                    rewrite = table + '_tab as ' + table
                                else:
                                    rewrite = table

                            sql2 = sql2 + rewrite
                    elif select_seen:
                        if is_subselect(item):
                            raise RuntimeError('Nested SELECT clauses are not supported; instead break into a named separate query')

                        if item.is_group:
                            for i in item.tokens:
                                if is_subselect(i):
                                    raise RuntimeError('Nested SELECT clauses are not supported; instead break into a named separate query')

                        if len(select_items):
                            if len(select_items) > 1:
                                if has_groupby:
                                    sql2 = sql2 + ', '.join([self.prune(str(item)), self._list_agg(self._const_agg(select_items)) + ' as _prov'])
                                else:
                                    sql2 = sql2 + ', '.join([self.prune(str(item)), self._const_agg(select_items) + ' as _prov'])
                            else:
                                if has_groupby:
                                    sql2 = sql2 + str(item) + ', ' + self._list_agg(select_items) + ' as _prov'
                                else:
                                    sql2 = sql2 + str(item) + ', ' + self.prune(select_items[0]) + ' as _prov'
                    else:
                        sql2 = sql2 + str(item)
                else:
                    if item.ttype is DML and item.value.upper() == 'SELECT':
                        sql2 = sql2 + str(item).upper()
                        select_seen = True
                    elif item.ttype is Keyword and item.value.upper() == 'FROM':
                        sql2 = sql2 + str(item).upper()
                        from_seen = True
                        select_seen = False
                    elif from_seen and item.ttype is Keyword and item.value.upper() == 'ON':
                        sql2 = sql2 + str(item).upper()
                        skip_token = True
                    elif item.ttype is Keyword and \
                        item.value.upper() in ['ORDER', 'GROUP', 'BY', 'WHERE', 'HAVING', 'GROUP BY', 'ORDER BY']:

                        sql2 = sql2 + str(item).upper()
                        from_seen = False
                        select_seen = False
                    elif item.ttype is Keyword:
                        sql2 = sql2 + str(item).upper()
                    else:
                        sql2 = sql2 + str(item)

        return sql2

    def prune(self, str):
        if ' as ' in str.lower():
            return str[0:str.lower().index(' as ')]
        else:
            return str

    def generate_prov_query_and_tables(self, sql: str) -> Tuple[Mapping[str, str], List[str]]:
        """
        From an SQL query, generates a sequence of definitions and a final query

        sql: original SQL query
        returns: a list of SQL DML and DDL statements. The last one will be the
                 rewritten query. Any additional statements will be to generate
                 intermediate provenance tables.
        """
        tables = extract_tables(sql)

        generate_tables: Mapping[str,str] = {}
        select_items = []

        has_groupby = False
        for statement in sqlparse.parse(sql):
            if not isinstance(statement, Statement):
                raise RuntimeError('Cannot get PROV query from something other than a select statement')

            for item in statement.tokens:
                if item.ttype is Keyword and item.value.upper() == 'GROUP' or item.value.upper() == 'GROUP BY':
                    has_groupby = True

        # Iterate through all tables, see if any are missing keys. If so
        # we will need to ensure there is a _uid provenance table for them.
        for tab in tables:
            if '=' in tab:
                # This is a parser issue, it includes ON clauses
                continue
            elif ' as ' in tab:
                # This is an aliased table
                
                # Actual table name
                tab_name = tab[0:tab.index(' ')]

                # Variable
                tab = tab[tab.rindex(' ') + 1]
            else:
                tab_name = tab

            tab_key = self.registry.get_key(tab_name)
            # For each relation, add a monotonically increasing ID
            # as ~index~, if there isn't already a key
            if len(tab_key.get_attributes()) == 1:
                for attr in tab_key.get_attributes():
                    if attr == Key.SPECIAL_INDEX:
                        if tab_name not in SchemaRegistry.table_map:
                            SchemaRegistry.table_map[tab_name] = \
                                'CREATE VIEW ' + tab_name + '_uid AS ' + \
                                ' SELECT *, array(monotonically_increasing_id()) AS _prov FROM ' + tab_name
                        select_items.append(tab + '._prov')
                    else:
                        select_items.append(tab + '.' + self.prune(attr) + " AS _prov")
            else:
                select_items.append('concat(' + ','.join(tab + '.' + self.prune(attr)) for attr in tab_key.get_attributes() + ' as _prov')

        ret = {}
        if len(SchemaRegistry.table_map):
            ret = self._create_provenance_tables(SchemaRegistry.table_map, sql)

        return (self._rewrite_sql_statement(sql, SchemaRegistry.table_map, select_items, has_groupby), ret)
        



