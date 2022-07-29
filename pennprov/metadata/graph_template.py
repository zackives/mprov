import pennprov.models.graph_script

from typing import List

class GraphTemplate:
    def is_leaf(self):
        return False

class IntermediateGraphTemplate(GraphTemplate):
    def __init__(self, children: List[GraphTemplate]):
        self.children = children

    def get_children(self) -> List[GraphTemplate]:
        return self.children

class LeafGraphTemplate(GraphTemplate):
    def __init__(self, value):
        self.value = value

    def is_leaf(self):
        return True

