import pennprov.models.graph_script

import datetime

from typing import List

class GraphComponent:
    def __init__(self, label):
        self.label = label

    def get_label(self):
        return self.get_label

    def is_leaf(self):
        return False

    def is_variable(self):
        return False

    def __repr__(self):
        return str(self.label)

class EdgeGraphTemplate(GraphComponent):    
    def __init__(self, src, label, dst):
        super().__init__(label)
        self.source = src
        self.destination = dst

    def get_source(self):
        return self.source

    def get_destination(self):
        return self.destination

class NodeGraphTemplate(GraphComponent):
    def __init__(self, value):
        super().__init__(value)

    def is_leaf(self):
        return True

class LiteralNodeGraphTemplate(NodeGraphTemplate):
    def __init__(self, value):
        super().__init__(value)

class BindingNodeGraphTemplate(NodeGraphTemplate):
    def __init__(self, value):
        super().__init__(value)
    
    def is_variable(self):
        return True

class GraphTemplate:
    nodes: List[NodeGraphTemplate] = []
    edges: List[EdgeGraphTemplate] = []

class GraphTemplateGenerator:
    def __init__(self, node_constructor, edge_constructor, agent):
        self.node_constructor = node_constructor
        self.edge_constructor = edge_constructor
        self.default_agent = agent


    def _gen_edge(self, edge):
        return EdgeGraphTemplate(edge['source'], edge['label'], edge['destination'])

    def generate_prov_derivation(self, input_bindings: List[str], process_binding:str, \
                                exec_time: datetime.datetime, output_binding: str, agent = None) -> GraphTemplate:
        ret = GraphTemplate()
        inputs = [BindingNodeGraphTemplate(inp) for inp in input_bindings]
        output_node = BindingNodeGraphTemplate(output_binding)
        ret.nodes.append(output_node)

        # Create an activity node
        activity_node = BindingNodeGraphTemplate(self.node_constructor(process_binding, {'provDmStartTime': exec_time}))
        ret.nodes.append(activity_node)

        if not agent:
            agent = self.default_agent

        agent_node = BindingNodeGraphTemplate(agent)
        ret.nodes.append(agent_node)

        activity_invokes = self._gen_edge(self.edge_constructor(activity_node, 'actedOnBehalfOf', agent_node))
        ret.edges.append(activity_invokes)

        activity_generates_outputs = self._gen_edge(self.edge_constructor(activity_node, 'wasGeneratedBy', output_node))
        ret.edges.append(activity_generates_outputs)
        
        agent_attribution = self._gen_edge(self.edge_constructor(output_node, 'wasAttributedTo', agent_node))
        ret.edges.append(agent_attribution)

        for inp_node in inputs:
            activity_uses_inputs = self._gen_edge(self.edge_constructor(inp_node, 'used', activity_node))
            ret.edges.append(activity_uses_inputs)
            derivation = self._gen_edge(self.edge_constructor(output_node, 'wasDerivedFrom', inp_node))
            ret.edges.append(derivation)

        return ret

