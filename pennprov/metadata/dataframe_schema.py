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

from ast import While
from tokenize import Whitespace
import pandas as pd
from pyspark.sql.types import StructField, StructType
from typing import ClassVar, List, Mapping, Any
from pyspark.sql.functions import monotonically_increasing_id
from sqlparse.sql import IdentifierList, Identifier, Statement
from sqlparse.tokens import Keyword, DML, Text, Token, Wildcard

from pennprov.queries.parse_sql import extract_tables,is_subselect

import sqlparse

class RelSchema:
    def __init__(self):
        self.elements: List[str] = []
        self.types: List[Any] = []

    def get_types(self):
        return self.types

    def get_attributes(self):
        return self.elements

    def get_typedefs(self):
        return [self.elements[i] + ': ' + self.types[i] for i in range(0, len(self.elements))]

    def __str__(self) -> str:
        return '(' + ', '.join([self.elements[i] + ':' + str(self.types[i]) for i in range(0, len(self.elements))]) + ')'

class Key(RelSchema):
    SPECIAL_INDEX = '~index~'

    def __init__(self, keylist, typlist):
        self.elements: List[str] = []
        self.types: List[Any] = []
        for item in keylist:
            self.elements.append(item)

        for typ in typlist:
            self.types.append(typ)

    def is_internal_index(self):
        return len(self.elements) == 1 and self.elements == Key.SPECIAL_INDEX

class PandasSchema(RelSchema):
    def __init__(self, df: pd.DataFrame):
        self.elements: List[str] = []
        self.types: List[Any] = []
        for column in df.columns:
            self.elements.append(column)

        for typ in df.dtypes:
            self.types.append(typ)

class SparkSchema(RelSchema):
    def __init__(self, sch: StructType):
        self.elements: List[str] = []
        self.types: List[Any] = []
        for column in sch.fields:
            self.elements.append(column.name)
            self.types.append(column.dataType)

class SchemaRegistry:
    DEFAULT_KEY = Key([Key.SPECIAL_INDEX], [int])
    table_map = {}
    created_tables = set()

    def __init__(self):
        self.catalog: Mapping[str,RelSchema] = {}
        self.keys: Mapping[str,Key] = {}


    def add(self, relation: str, primary_key: Key):
        self.catalog[relation] = primary_key

    def remove(self, relation):
        del self.catalog[relation]

    def get_schema(self, relation:str) -> Key:
        return self.catalog[relation]

    def add_pandas(self, name: str, df: pd.DataFrame):
        self.catalog[name] = PandasSchema(df)
        self.keys[name] = [Key.SPECIAL_INDEX]

    def set_keys(self, name: str, keys: List[str], types: List[str]):
        self.keys[name] = Key(keys, types)

    def add_spark(self, name: str, sch: StructType):
        self.catalog[name] = SparkSchema(sch)
        self.keys[name] = [Key.SPECIAL_INDEX]

    def get_keys(self, name: str) -> Key:
        if name in self.keys:
            return self.keys[name]
        else:
            return SchemaRegistry.DEFAULT_KEY

    def create_tables(self, table_map: Mapping[str, str], sql: str) -> List[str]:
        ret = []
        for table in table_map.keys():
            if table not in SchemaRegistry.created_tables:
                sql1 = 'CREATE TABLE ' + table + "_tab LIKE " + table + '_uid STORED AS PARQUET'
                sql2 = table_map[table]

                ret.append(sql2)
                ret.append(sql1)
                SchemaRegistry.created_tables.add(table)
        return ret

    def get_rewrite(self, sql: str, table_map, select_items, has_groupby) -> str:
        # TODO: go through sql, replace each table in the FROM clause
        # that matches table, with table_tab
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
                                            rewrite = rewrite + str(table)
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
                                select_str = ', '.join(select_items)
                                if has_groupby:
                                    sql2 = sql2 + ', '.join([str(item), 'collect_list(concat(' + select_str + ')) as _prov'])
                                else:
                                    sql2 = sql2 + ', '.join([str(item), 'concat(' + select_str + ') as _prov'])
                            else:
                                if has_groupby:
                                    sql2 = sql2 + str(item) + ', collect_list(' + select_items[0] + ') as _prov'
                                else:
                                    sql2 = sql2 + str(item) + ', ' + select_items[0] + ' as _prov'
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

        # Repeat recursively
        return sql2

    def get_prov_query_list(self, sql: str) -> List[str]:
        tables = extract_tables(sql)

        select_items = []

        ret = []

        has_groupby = False
        for statement in sqlparse.parse(sql):
            if not isinstance(statement, Statement):
                raise RuntimeError('Cannot get PROV query from something other than a select statement')

            for item in statement.tokens:
                if item.ttype is Keyword and item.value.upper() == 'GROUP' or item.value.upper() == 'GROUP BY':
                    has_groupby = True


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

            tab_key = self.get_keys(tab_name)
            # For each relation, add a monotonically increasing ID
            # as ~index~, if there isn't already a key
            for attr in tab_key.get_attributes():
                if attr == Key.SPECIAL_INDEX:
                    if tab_name not in SchemaRegistry.table_map:
                        SchemaRegistry.table_map[tab_name] = \
                            'CREATE VIEW ' + tab_name + '_uid AS ' + \
                            ' SELECT *, monotonically_increasing_id() AS _prov FROM ' + tab_name
                    select_items.append(tab + '._prov')
                else:
                    select_items.append(tab + '.' + attr)

        ret = []
        if len(SchemaRegistry.table_map):
            # print ('Substitute tables for Skolem tables:')
            ret = self.create_tables(SchemaRegistry.table_map, sql)

        # # For each join, output the cat of those indices as the prov
        # if len(select_items):
        #     print ('Additional SELECT list items:')
        #     print (select_items)
        # For each groupby, output the nested list of those indices as the prov

        # Repeat recursively
        ret.append(self.get_rewrite(sql, SchemaRegistry.table_map, select_items, has_groupby))

        return ret
        

sr = SchemaRegistry()
df = pd.DataFrame([{'x': 3, 'y': 2}, {'x': 4, 'z': 'str'}])
sr.add_pandas('df', df)
sr.add_pandas('b', df)
sr.set_keys('b', ['x'], [str])
print('Dataframe keys: %s'%sr.get_keys('df'))

print('Prov queries: %s'%sr.get_prov_query_list('select a, d as coffee from a, b where a.x = b.y'))

print('Prov queries: %s'%sr.get_prov_query_list('select a, d as coffee, monotonically_increasing_id() from a AS t, b, c where t.x = b.y and b.z = c.d'))

print('Prov queries: %s'%sr.get_prov_query_list('select * from a AS t left join b AS G on a.x = b.y, c group by w'))

print('Prov queries: %s'%sr.get_prov_query_list('select * from a where x = 5'))

print('Prov queries: %s'%sr.get_prov_query_list('select * from a where false'))

try:
    print('Prov queries: %s'%sr.get_prov_query_list('select *, (select * from c) from a where false'))
except:
    print('Successfully trapped nested SELECT clause')

try:
    print('Prov queries: %s'%sr.get_prov_query_list('select * from a AS t join (select * from c) AS G on a.x = b.y, c group by w'))
    raise RuntimeError('Unexpected: let a nested FROM query expression through')
except:
    print('Successfully trapped nested FROM clause')
