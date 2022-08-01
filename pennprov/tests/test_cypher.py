from pennprov.cypher.cypher import CypherInterface 
import pennprov.sql.sql_provenance
import uuid

import datetime

from pennprov.metadata.graph_template import GraphTemplate, GraphTemplateGenerator

class SimpleGraph:
    nodes = {}
    edges = []

    def node_gen(value, properties):
        node_id = uuid.uuid4()
        SimpleGraph.nodes[node_id] = {'value': value, 'properties': properties}
        return SimpleGraph.nodes[node_id]

    def edge_gen(src, label, trg):
        edge = {'source': src, 'label': label, 'destination': trg}
        SimpleGraph.edges.append(edge)
        return edge


ci = CypherInterface()

gtg = GraphTemplateGenerator(SimpleGraph.node_gen, SimpleGraph.edge_gen, SimpleGraph.node_gen('agent',{}))

def test_parser():
    ci.parse('MATCH (n) RETURN count(n)')


def test_match():
    input = [SimpleGraph.node_gen('node_label', {'value1': 3})]
    output = SimpleGraph.node_gen('output_label', {'value2': 'x'})
    process = SimpleGraph.node_gen('program', {'parm1': '3x'})

    template = gtg.generate_prov_derivation(input, process, datetime.datetime.now(), output)

    print (gtg)