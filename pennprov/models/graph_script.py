from doctest import script_from_examples
from enum import Enum
from typing import List, Any, Mapping, Tuple
import uuid
from uuid import UUID

import logging

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
    CONCAT3 = 31
    REF = 32

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
        elif isinstance(id, UUID):
            self.id = id
        else:
            self.id = GraphScript.get_id_from_key(str(id))

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

    def __str__(self) -> str:
        if len(self.args) == 1 and isinstance(self.args[0], Tuple) and \
            len(self.args[0]) == 1 and isinstance(self.args[0][0], UUID):
            return str(self.id) + ": " + str(self.op) + " " + self.args[0][0].hex
        else:
            return Cmd.__str__(self)

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
        Cmd.__init__(self, Op.EDGE, [frominx, labinx, toinx], GraphScript.get_id_from_key(str((frominx, toinx))))

class EdgeLabCmd(Cmd):
    def __init__(self, frominx, label, toinx):
        # type: (int, str, int) -> None
        Cmd.__init__(self, Op.EDGE_LAB, [frominx, label, toinx], GraphScript.get_id_from_key(str((frominx, label,toinx))))

class CatCmd(Cmd):
    def __init__(self, left_interval, right_interval):
        # type: (int, List[Any], List[Any]) -> None
        Cmd.__init__(self, Op.CONCAT, [left_interval, right_interval], GraphScript.get_id())

class Cat3Cmd(Cmd):
    def __init__(self, left_interval, mid_interval, right_interval):
        # type: (int, List[Any], List[Any]) -> None
        Cmd.__init__(self, Op.CONCAT3, [left_interval, mid_interval, right_interval], GraphScript.get_id())

class RefCmd(Cmd):
    def __init__(self, prev_cmd):
        # type: (int, UUID) -> None
        Cmd.__init__(self, Op.REF, [prev_cmd])

    def __str__(self) -> str:
        return str(self.id) + ": " + str(self.op) + " " + str([str(x)+ " " for x in self.args])

class CmdLog:
    # Actual history log, to push to DB
    cmd_log: List[UUID] = []

    def __init__(self, store: ProvenanceStore):
        pass

    def append(self, command: Cmd):
        self.cmd_log.append(command)

    def apply(self):
        print("** Commands **")
        for item in self.cmd_log:
            print("%s"%item)
class GraphScript:
    # Bounded LRU queue, from ordering -> hash
    cmd_list: List[UUID] = []

    cmd_log: CmdLog

    # Hash --> command
    cmd_hash: Mapping[UUID,Cmd] = {}
    cmd_stack: Mapping[UUID,List[Any]] = {}

    # The list of commands that we are queuing up
    working_sequence: List[UUID] = []

    MAX: int = 1024              # max entries in command LRU queue

    def __init__(self, store: ProvenanceStore):
        self.cmd_log = CmdLog(store)

    def get_id() -> UUID:
        """
        Returns a new UUID
        """
        return uuid.uuid4()

    def get_id_from_key(key: Any) -> UUID:
        """
        Returns a hash of the provided key
        """
        return uuid.uuid5(uuid.NAMESPACE_URL, key)


    def evict(self) -> None:
        """
        If the command list has exceeded MAX length, evicts
        the oldest item in the queue, including its stack and command
        """
        while len(self.cmd_list) > self.MAX:
            cmd = self.cmd_list[-1]
            del self.cmd_list[-1]
            del self.cmd_stack[cmd]
            del self.cmd_hash[cmd]

    def add_or_promote_command(self, the_id: UUID) -> bool:
        """
        Given a UUID, promote it to the top of the LRU list. Returns True
        if we are promoting, False if it's a new command.
        """
        if the_id in self.cmd_list:
            self.cmd_list.remove(the_id)
            self.cmd_list.append(the_id)
            return True
        else:
            self.cmd_list.append(the_id)
            self.evict()
            return False

    def create_command(self, cmd: Cmd) -> Tuple[UUID, bool]:
        """
        Given the Cmd and its unique signature -- creates
        a new Cmd with a new UUID, or returns the UUID of a previous
        occurrence.
        """
        id = cmd.get_id()

        if id not in self.cmd_hash:
            self.cmd_hash[id] = cmd
            return (id, False)
        else:
            return (id, True)

    def create_command(self, cmd: Cmd) -> Tuple[UUID, bool]:
        """
        Given the Cmd and its unique signature -- creates
        a new Cmd with a new UUID, or returns the UUID of a previous
        occurrence.
        """
        id = cmd.get_id()

        if id not in self.cmd_hash:
            self.cmd_hash[id] = cmd
            return (id, False)
        else:
            return (id, True)

    def apply_script(self, target: ProvenanceStore, start:int=0, end:int=-1) -> None:
        self.cmd_log.apply()

    def flush_working_sequence(self):
        # For now, dequeue all items in the working sequence
        # TODO: reorder, merge the PUSHes, add CONCAT and appropriate
        # re-indexing

        # Trigger a CONCAT each time we have a new PUSH that doesn't 
        # match an existing sequence?
        if len(self.working_sequence) == 1:
            for item in self.working_sequence:
                self.cmd_log.append(self.cmd_hash[item])
        elif len(self.working_sequence):
            for item in self.working_sequence:
                self.cmd_log.append(RefCmd(self.cmd_hash[item]))

        self.working_sequence.clear()


    def add_node(self, id: UUID, label: str, values: Tuple[Any]) -> UUID:
        """
        Create a new node with a given id and tuple
        """
        arg_stack: List[Tuple] = []
        arg_stack.append([id, values])

        bind_cmd,ru1 = self.create_command(PushCmd([id,values]))
        ru = "Reuse " if ru1 else ""
        print (ru + str(self.cmd_hash[bind_cmd]))

        self.add_or_promote_command(bind_cmd)
        if ru1:
            self.working_sequence.append(bind_cmd)
        else:
            self.cmd_log.append(self.cmd_hash[bind_cmd])

        node_cmd,ru2 = self.create_command(NodeLabCmd(0, label))
        ru = "Reuse " if ru2 else ""
        self.add_or_promote_command(node_cmd)
        if ru2:
            self.working_sequence.append(node_cmd)
        else:
            self.cmd_log.append(self.cmd_hash[node_cmd])
        print (ru + str(self.cmd_hash[node_cmd]))

        # TODO: this should only be unique if the binding is unique
        cat_cmd,ru3 = self.create_command(CatCmd((0,), (1,)))
        ru = "Reuse " if ru3 else ""

        # FOR now we are greedy and always do at least the CAT
        #if not ru1 or not ru2:# or not ru3:
        if not self.add_or_promote_command(cat_cmd):
            self.cmd_stack[cat_cmd] = arg_stack
            print ("Args: %s"%arg_stack)
        else:
            self.working_sequence.append(cat_cmd)
            self.cmd_log.append(self.cmd_hash[cat_cmd])

        print (ru + str(self.cmd_hash[cat_cmd]))

        self.flush_working_sequence()

        return node_cmd

    def add_edge(self, source: UUID, label: str, dest: UUID) -> UUID:
        """
        Adds an edge between the source and node with a given label.
        Current version does NOT have properties but this could be extended.
        """
        arg_stack: List[Tuple] = []
        arg_stack.append((dest,))
        arg_stack.append((source,))

        bind1_cmd,ru1 = self.create_command(PushCmd((dest,)))
        ru = "Reuse " if ru1 else ""
        print (ru + str(self.cmd_hash[bind1_cmd]))
        self.add_or_promote_command(bind1_cmd)
        if ru1:
            self.working_sequence.append(bind1_cmd)
        else:
            self.cmd_log.append(self.cmd_hash[bind1_cmd])

        bind2_cmd,ru2 = self.create_command(PushCmd((source,)))
        ru = "Reuse " if ru2 else ""
        print (ru + str(self.cmd_hash[bind2_cmd]))
        self.add_or_promote_command(bind2_cmd)
        if ru2:
            self.working_sequence.append(bind2_cmd)
        else:
            self.cmd_log.append(self.cmd_hash[bind2_cmd])

        edge_cmd,ru3 = self.create_command(EdgeCmd(0, 1, label))
        ru = "Reuse " if ru3 else ""
        print (ru + str(self.cmd_hash[edge_cmd]))
        self.add_or_promote_command(edge_cmd)
        if ru3:
            self.working_sequence.append(edge_cmd)
        else:
            self.cmd_log.append(self.cmd_hash[edge_cmd])

        cat_cmd,ru4 = self.create_command(Cat3Cmd((1,), (2,), [0]))
        ru = "Reuse " if ru4 else ""

        # FOR now we are greedy and always do at least the CAT
        #if not ru1 or not ru2 or not ru3:
        if not self.add_or_promote_command(cat_cmd):
            self.cmd_stack[cat_cmd] = arg_stack
            print ("Args: %s"%arg_stack)
        else:
            self.working_sequence.append(cat_cmd)
            self.cmd_log.append(self.cmd_hash[cat_cmd])
        print (ru + str(self.cmd_hash[cat_cmd]))

        self.flush_working_sequence()

        return edge_cmd

class ProvenanceScript(ProvenanceStore):
    script: GraphScript
    sub_store: ProvenanceStore

    def __init__(self, sub_store):
        # type: (ProvenanceStore) -> None
        self.sub_store = sub_store
        self.script = GraphScript(sub_store)

    
    def add_node(self, db, resource, label, skolem_args):
        # type: (cursor, str, str, List[Any]) -> None

        # Use an ID field as a key, if it exists
        if 'id' in skolem_args:
            the_id = GraphScript.get_id_from_key(label + '.' + skolem_args.id)
        else:
            the_id = GraphScript.get_id_from_key('.'.join([label, str((skolem_args))]))

        print('Node: %s: (%s,%s)' %(the_id,label,str(skolem_args)))
        self.script.add_node(the_id, label, skolem_args)
        return the_id

    def add_edge(self, db, resource, source, label, dest):
        # type: (cursor, str, str, str, str) -> None
        self.script.add_edge(source, label, dest)
        return 1

    def add_nodeprop(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, Any, int) -> None
        return 1

    def flush(self, db, resource):
        self.script.apply_script(self.sub_store)
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
    input1 = store.add_node(db, "mprov", "entity", ('stream1', 1+offset,3+offset,'x'))
    input2 = store.add_node(db, "mprov", "entity", ('stream2', 2+offset,4+offset,'y'))
    prog1_exec1 = store.add_node(db, "mprov", 'activity', ('prog1','7-1-2022'))
    output1 = store.add_node(db, "mprov", "entity", ('stream3', 3+offset,5+offset,'z'))
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
    input_common = store.add_node(db, "mprov", "entity", ('file1',))
    prog1_source = store.add_node(db, 'mprov', 'entity', ('prog1.c', '1-1-1980'))

    write_motif(db, store, prog1_source, input_common, 1)
    write_motif(db, store, prog1_source, input_common, 2)
    write_motif(db, store, prog1_source, input_common, 3)

    store.flush(db, "mprov")

simple_test(None, ProvenanceScript(ProvenanceStore()))