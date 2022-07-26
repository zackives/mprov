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

import pandas as pd
from pyspark.sql.types import StructField, StructType
from typing import ClassVar, List, Mapping, Any
from pyspark.sql.functions import monotonically_increasing_id

from pennprov.queries.parse_sql import extract_tables

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

    def get_prov_query(self, sql: str) -> str:
        tables = extract_tables(sql)

        table_map = {}
        extra_statements = []

        clauses = []

        select_items = []
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
            for attr in tab_key.get_attributes():
                if attr == Key.SPECIAL_INDEX:
                    if tab_name not in table_map:
                        table_map[tab_name] = \
                            'CREATE VIEW ' + tab_name + '_uid AS ' + \
                            ' SELECT *, monotonically_increasing_id() AS _sk FROM ' + tab_name
                        extra_statements.append(table_map[tab_name])
                    select_items.append(tab + '._sk')
                else:
                    select_items.append(tab + '.' + attr)

        # For each relation, add a monotonically increasing ID
        # as ~index~

        if len(extra_statements):
            print ("Extra SQL statements:")
            for es in extra_statements:
                print (es)

        if len(table_map):
            print ('Substitute tables for Skolem tables:')
            print (list(table_map.keys()))

        # For each join, output the cat of those indices as the prov
        if len(select_items):
            print ('Additional SELECT list items:')
            print (select_items)
        # For each groupby, output the nested list of those indices as the prov

        # Repeat recursively
        

sr = SchemaRegistry()
df = pd.DataFrame([{'x': 3, 'y': 2}, {'x': 4, 'z': 'str'}])
sr.add_pandas('df', df)
sr.add_pandas('b', df)
sr.set_keys('b', ['x'], [str])
print('Dataframe keys: %s'%sr.get_keys('df'))

print('Prov query: %s'%sr.get_prov_query('select * from a AS t join b AS G on a.x = b.y, c'))