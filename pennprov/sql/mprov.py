import pennprov
from pennprov.connection.mprov_connection import MProvConnection
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

