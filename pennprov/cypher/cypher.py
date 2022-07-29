#pip3 install --global-option=build_ext --global-option="-I/opt/homebrew/include" --global-option="-L/opt/homebrew/lib" libcypher-parser-python

#import pennprov.metadata.graph_template
#import pennprov.models.graph_script

import pycypher

import pennprov.sql.sql_provenance
from pennprov.metadata.catalog_manager import Catalog

class Variable:
    def __init__(self, var_name):
        self.var = var_name

class Label:
    def __init__(self, label):
        self.label = label

class Node:
    def __init__(self, opt_name, opt_label):
        return

class Edge:
    def __init__(self, opt_name, opt_label):
        return

class CypherInterface:
    catalog: Catalog = Catalog()

    def execute(self, cypher_query: str):
        return []

    def parse(self, cypher_query:str):
        parsed, dict = pycypher.parse(cypher_query)

        if not parsed:
            raise RuntimeError('Failed to parse')
        else:
            return dict

ci = CypherInterface()

ci.parse("MATCH (n) RETURN Count(n)")