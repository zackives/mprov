from doctest import script_from_examples
from enum import Enum
from typing import List, Any, Mapping
import uuid
from uuid import UUID

from pennprov.connection.provenance_store import ProvenanceStore

class Op(Enum):
    PUSH = 0
    SET = 1
    POP = 2
    DEL = 3
    XCH = 4
    NODE = 10
    NODE_LAB = 11
    EDGE = 20
    EDGE_LAB = 21
    CONCAT = 30
    REF = 31

class Cmd:
    op = None            # type: Op
    args = None          # Type: List[None]
    id = None

    def __init__(self, op, args, id=None):
        # type: (Op, List[Any], UUID) -> None
        self.op = op
        self.args = args
        if not id:
            self.id = GraphScript.get_id()
        else:
            self.id = id

    def get_id(self):
        return self.id

    def __str__(self) -> str:
        return str(self.id) + ": " + str(self.op) + " " + str(self.args)

class PushCmd(Cmd):
    def __init__(self, arg):
        # type: (UUID|str) -> None
        if isinstance(arg, list):
            Cmd.__init__(self, Op.PUSH, arg, arg[0])
        else:
            Cmd.__init__(self, Op.PUSH, [arg], arg)

class SetCmd(Cmd):
    def __init__(self, arg, pos):
        # type: (UUID|str, int) -> None
        Cmd.__init__(self, Op.SET, [arg, pos])

class PopCmd(Cmd):
    def __init__(self):
        # type: () -> None
        Cmd.__init__(self, Op.POP, [])

class DelCmd(Cmd):
    def __init__(self, pos):
        # type: (int) -> None
        Cmd.__init__(self, Op.DEL, [pos])

class XchCmd(Cmd):
    def __init__(self, pos1, pos2):
        # type: (int, int) -> None
        Cmd.__init__(self, Op.XCH, [pos1, pos2])

class NodeCmd(Cmd):
    def __init__(self, idinx, labinx):
        # type: (int, int) -> None
        Cmd.__init__(self, Op.NODE, [idinx, labinx], GraphScript.get_id_from_key(str((idinx,labinx))))

class NodeLabCmd(Cmd):
    def __init__(self, idinx, label):
        # type: (int, str) -> None
        Cmd.__init__(self, Op.NODE_LAB, [idinx, label], GraphScript.get_id_from_key(str(idinx) + ',' + label))

class EdgeCmd(Cmd):
    def __init__(self, frominx, labinx, toinx):
        # type: (int, int, int) -> None
        Cmd.__init__(self, Op.EDGE, [frominx, labinx, toinx])

class EdgeLabCmd(Cmd):
    def __init__(self, frominx, label, toinx):
        # type: (int, str, int) -> None
        Cmd.__init__(self, Op.EDGE_LAB, [frominx, label, toinx])

class CatCmd(Cmd):
    def __init__(self, left_interval, right_interval):
        # type: (int, List[Any], List[Any]) -> None
        Cmd.__init__(self, Op.CONCAT, [left_interval, right_interval])

class RefCmd(Cmd):
    def __init__(self, prev_cmd):
        # type: (int, UUID) -> None
        Cmd.__init__(self, Op.REF, [prev_cmd])

class GraphScript:
    # Bounded LRU queue, from ordering -> hash
    cmd_list = []           # type: List[UUID]
    # Hash --> command
    cmd_hash = {}           # type: Mapping[UUID,Cmd]

    working_set = []        # type: List[UUID]

    # Should it be a list of lists? a tree?

    MAX = 1024

    def get_id():
        # type: () -> UUID
        return uuid.uuid4()

    def get_id_from_key(key):
        # type: (Any) -> UUID
        return uuid.uuid5(uuid.NAMESPACE_URL, key)


    def evict(self):
        if len(self.cmd_list) > self.MAX:
            pass

    def append_command(self, cmd):
        # type: (Cmd) -> UUID
        id = cmd.get_id()
        self.cmd_list.append(id)
        if id not in self.cmd_hash:
            self.cmd_hash[id] = cmd
        else:
            print('Reusing %s'%(self.cmd_hash[id]))

        self.evict()

        return id

    ## Find a binding in the working set, and return its index if it's there
    def add_or_lookup(self, the_id):
        # type: (UUID) -> int
        if the_id not in self.working_set:
            self.working_set.append(the_id)
            return (len(self.working_set) - 1, False)
        else:
            inx = self.working_set.index(the_id)
            return (inx, True)

    def reuse_command_by_index(self, inx_pos):
        # type: (int) -> UUID
        hash  = self.cmd_list[inx_pos]
        self.cmd_list.remove(hash)
        self.cmd_list.append(hash)
        return hash

    def discard_command_by_index(self, inx_pos):
        # type: (int) -> None
        hash  = self.cmd_list[inx_pos]
        self.cmd_list.remove(hash)
        del self.cmd_hash[hash]

    def apply_script(self, target, start=0, end=-1):
        # type: (ProvenanceStore, int, int) -> None
        pass

    def add_node(self, id, label, values):
        #binding,is_reused = self.add_or_lookup(id)

        bind_cmd = self.append_command(PushCmd([id,values]))
        print (str(self.cmd_hash[bind_cmd]))
        node_cmd = self.append_command(NodeLabCmd(0, label))
        print (str(self.cmd_hash[node_cmd]))

        return node_cmd

    def add_edge(self, source, label, dest, values):
        return

class ProvenanceScript(ProvenanceStore):
    script = GraphScript()
    sub_store = None

    def __init__(self, sub_store):
        # type: (ProvenanceStore) -> None
        self.sub_store = sub_store

    
    def add_node(self, db, resource, label, skolem_args):
        # type: (cursor, str, str, List[Any]) -> None

        # Use an ID field as a key, if it exists
        if 'id' in skolem_args:
            the_id = GraphScript.get_id_from_key(label + '.' + skolem_args.id)
        else:
            the_id = GraphScript.get_id()

        print('Node: %s: (%s,%s)' %(the_id,label,str(skolem_args)))
        self.script.add_node(the_id, label, skolem_args)
        return 1

    def add_edge(self, db, resource, source, label, dest):
        # type: (cursor, str, str, str, str) -> None
        self.script.add_edge(source, label, dest, [])
        return 1

    def add_nodeprop(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, Any, int) -> None
        return 1

    def flush(self, db, resource):
        self.sub_store.flush(db, resource)
        return

    def reset(self):
        self.sub_store.reset()
        return

    def create_tables(self, cursor):
        # type: (cursor) -> None
        self.sub_store.create_tables(cursor)

    def clear_tables(self, db, graph):
        # type: (cursor, str) -> None
        self.sub_store.clear_tables(db, graph)

    def get_provenance_data(self, db, resource, token):
        # type: (cursor, str, str) -> List[Dict]
        return

    def get_connected_to(self, db, resource, token, label1):
        # type: (cursor, str, str, str) -> List[str]
        return

    def get_connected_from(self, db, resource, token, label1):
        # type: (cursor, str, str, str) -> List[str]
        return

    def get_connected_to_labeled(self, db, resource, token, label1):
        # type: (cursor, str, str, str) -> List[Tuple(str,str)]
        return

    def get_connected_from_labeled(self, db, resource, token, label1):
        # type: (cursor, str, str, str) -> List[Tuple(str,str)]
        return

    def get_edges(self, db, resource):
        #type: (cursor, str) -> List[Tuple]
        return []

    def get_nodes(self, db, resource):
        #type: (cursor, str) -> List[Dict]
        return []



######################## Simple Test Script #######################


def write_motif(db, store, prog1_source, input_common, offset):
    input1 = store.add_node(db, "mprov", "entity", ['stream1', 1+offset,3+offset,'x'])
    input2 = store.add_node(db, "mprov", "entity", ['stream2', 2+offset,4+offset,'y'])
    prog1_exec1 = store.add_node(db, "mprov", 'activity', ['prog1','7-1-2022'])
    output1 = store.add_node(db, "mprov", "entity", ['stream3', 3+offset,5+offset,'z'])
    edge1 = store.add_edge(db, 'mprov', prog1_exec1, 'used', input1)
    edge2 = store.add_edge(db, 'mprov', prog1_exec1, 'used', input2)
    edge2 = store.add_edge(db, 'mprov', prog1_exec1, 'used', input_common)
    edge3 = store.add_edge(db, 'mprov', output1, 'wasGeneratedBy', prog1_exec1)
    edge4 = store.add_edge(db, 'mprov', prog1_exec1, 'used', prog1_source)
    edge5 = store.add_edge(db, 'mprov', output1, 'wasDerivedFrom', input1)
    edge5 = store.add_edge(db, 'mprov', output1, 'wasDerivedFrom', input2)
    edge5 = store.add_edge(db, 'mprov', output1, 'wasDerivedFrom', input_common)

def simple_test(db, store):
    # These nodes are used across multiple motifs
    input_common = store.add_node(db, "mprov", "entity", ['file1'])
    prog1_source = store.add_node(db, 'mprov', 'entity', ['prog1.c', '1-1-1980'])

    write_motif(db, store, prog1_source, input_common, 1)
    write_motif(db, store, prog1_source, input_common, 2)
    write_motif(db, store, prog1_source, input_common, 3)

simple_test(None, ProvenanceScript(ProvenanceStore()))