import pandas as pd
from typing import ClassVar, List, Mapping, Any, Tuple

from pyspark.sql.types import StructType

from pennprov.metadata.dataframe_schema import SparkSchema, PandasSchema, RelSchema, Key

import logging

class SchemaRegistry:
    DEFAULT_KEY = Key([Key.SPECIAL_INDEX], [int])
    table_map = {}
    created_tables = set()

    def __init__(self):
        self.catalog: Mapping[str,RelSchema] = {}
        self.keys: Mapping[str,Key] = {}


    def add_schema(self, relation: str, schema: RelSchema):
        logging.debug('Adding relation key %s'%relation)
        self.catalog[relation] = schema

    def remove_schema(self, relation):
        del self.catalog[relation]

    def get_schema(self, relation:str) -> RelSchema:
        return self.catalog[relation]

    def add_pandas_dataframe(self, name: str, df: pd.DataFrame):
        logging.debug('Adding Pandas dataframe %s'%name)
        self.catalog[name] = PandasSchema(df)
        self.keys[name] = [Key.SPECIAL_INDEX]

    def add_spark_dataframe(self, name: str, sch: StructType):
        logging.debug('Adding Spark dataframe %s'%name)
        self.catalog[name] = SparkSchema(sch)
        self.keys[name] = [Key.SPECIAL_INDEX]

    def set_key(self, name: str, keys: List[str], types: List[str]):
        self.keys[name] = Key(keys, types)
        logging.debug('Set key %s: %s'%(name,self.keys[name]))

    def get_key(self, name: str) -> Key:
        if name in self.keys:
            return self.keys[name]
        else:
            return SchemaRegistry.DEFAULT_KEY
