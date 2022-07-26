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

import logging

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

