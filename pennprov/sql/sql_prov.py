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
import pennprov
from pennprov.connection.mprov import MProvConnection
import hashlib, binascii
import sqlparse
import pyspark

class SqlProvenance:
    tab_to_schema = {}
    mprov = None

    def __init__(self, mprov_conn):
        # type: (MProvConnection) -> None
        self.tab_to_schema = {}
        self.mprov = mprov_conn

    def query_to_entity(self, query):
        # type: (str) -> pennprov.QualifiedName
        """
        Takes an SQL query and gets a QName to an entity
        :param query:
        :return:
        """
        return self.mprov.store_code(query)

    def create_or_replace_temp_view(self, py_name, sql_name):
        # type: (str, str) -> None
        """
        Replacement for spark.createOrReplaceTempView(), logs
        naming and schema info

        :param py_name: Python variable
        :param sql_name: Table name for SQL
        :return:
        """
        self.tab_to_schema[sql_name] = py_name.schema
        py_name.createOrReplaceTempView(sql_name)

        print(self.tab_to_schema[sql_name])

