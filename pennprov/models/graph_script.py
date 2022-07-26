from doctest import script_from_examples
from enum import Enum
from typing import List, Any, Mapping, Tuple, MutableSet
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
    NODE_LAB = 11
    EDGE_LAB = 21
    CONCAT = 30
    CONCAT3 = 31
    REF = 32

class Cmd:
    def __init__(self, op: Op, args: List[Any], id:UUID=None):
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

class PopCmd(Cmd):
    def __init__(self, arg):
        # type: (UUID|str) -> None
        if isinstance(arg, list):
            Cmd.__init__(self, Op.POP, arg, "p" + str(arg[0]))
        else:
            Cmd.__init__(self, Op.POP, [arg], "p" + str(arg))

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

class DelCmd(Cmd):
    def __init__(self, pos):
        # type: (int) -> None
        Cmd.__init__(self, Op.DEL, [pos])

class XchCmd(Cmd):
    def __init__(self, pos1, pos2):
        # type: (int, int) -> None
        Cmd.__init__(self, Op.XCH, [pos1, pos2])

class NodeLabCmd(Cmd):
    def __init__(self, idinx, label):
        # type: (int, str) -> None
        Cmd.__init__(self, Op.NODE_LAB, [idinx, label], GraphScript.get_id_from_key(str(idinx) + ',' + label))

class EdgeLabCmd(Cmd):
    def __init__(self, frominx, label, toinx):
        # type: (int, str, int) -> None
        Cmd.__init__(self, Op.EDGE_LAB, [frominx, label, toinx], GraphScript.get_id_from_key(str((frominx, label,toinx))))

class CatCmd(Cmd):
    def __init__(self, left_op, right_op):
        # type: (int, UUID, UUID) -> None
        Cmd.__init__(self, Op.CONCAT, [left_op, right_op], GraphScript.get_id_from_key(str(left_op) + str(right_op)))

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

    def __init__(self, store: ProvenanceStore):
        # Actual history log, to push to DB
        self.cmd_log: List[UUID] = []

    def append(self, command: Cmd):
        self.cmd_log.append(command)

    def remove(self, index: int):
        del self.cmd_log[-index - 1]

    def apply(self):
        print("** %d commands **" %len(self.cmd_log))
        for item in self.cmd_log:
            print("%s"%item)


class GraphScript:
    MAX: int = 1024              # max entries in command LRU queue

    def __init__(self, store: ProvenanceStore):
        self.cmd_log: CmdLog = CmdLog(store)
        
        # Bounded LRU queue, from ordering -> hash
        self.cmd_list: List[UUID] = []

        # Hash --> command
        self.cmd_hash: Mapping[UUID,Cmd] = {}
        self.cmd_stack: Mapping[UUID,List[Any]] = {}

        self.cmd_argsize: Mapping[UUID,int] = {}

        # The list of commands that we are queuing up
        self.working_sequence: List[UUID] = []

        self.data_entries: List[UUID] = []


    @classmethod
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
            del self.cmd_argsize[cmd]

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

    def create_command(self, cmd: Cmd, argsize: int = 1) -> Tuple[UUID, bool]:
        """
        Given the Cmd and its unique signature -- creates
        a new Cmd with a new UUID, or returns the UUID of a previous
        occurrence.
        """
        id = cmd.get_id()

        if id not in self.cmd_hash:
            self.cmd_hash[id] = cmd
            self.cmd_argsize[id] = argsize
            return (id, False)
        else:
            return (id, True)

    def create_command(self, cmd: Cmd, argsize: int = 1) -> Tuple[UUID, bool]:
        """
        Given the Cmd and its unique signature -- creates
        a new Cmd with a new UUID, or returns the UUID of a previous
        occurrence.
        """
        id = cmd.get_id()

        if id not in self.cmd_hash:
            self.cmd_hash[id] = cmd
            self.cmd_argsize[id] = argsize
            return (id, False)
        else:
            return (id, True)

    def apply_script(self, target: ProvenanceStore, start:int=0, end:int=-1) -> None:
        self.cmd_log.apply()


    # def merge_bindings(self, working_list: List[Cmd]) -> List[Cmd]:
    #     updated_list = working_list.copy()
    #     binding_list: List[Cmd] = []
    #     updated_command_list: List[Cmd] = []

    #     # print ('Merging %s'%updated_list)

    #     # Collect each item
    #     for item in working_list:
    #         if isinstance(self.cmd_hash[item], PushCmd):
    #             if item not in binding_list:
    #                 binding_list.append(item)
    #                 # print (' Added push item to stack %s' %item)
    #                 updated_command_list.append(item)

    #     for first_k in range(1, len(binding_list)+1):
    #         # For each prefix of the binding list, collect
    #         # all commands that specifically reference the bindings
    #         # in that prefix
    #         args = binding_list[0:first_k]
    #         # print("Studying %s" %args)
    #         inx = 0
    #         working_stack = []
    #         while inx < len(updated_list):
    #             command = self.cmd_hash[updated_list[inx]]

    #             if isinstance(command, PushCmd):
    #                 # Drop the PUSH commands
    #                 #print ('***  PUSH %s %s'%(command,command.args))
                    
    #                 ### Only continue expanding the stack if we are allowed
    #                 ### this many binding parameters!!!
    #                 if command.args[0] in working_stack or \
    #                 len(set(working_stack)) < len(args):
    #                     working_stack.append(command.args[0])
    #                 else:
    #                     break
    #                 inx = inx + 1
    #             elif isinstance(command, NodeLabCmd):
    #                 # TODO: rewrite with the correct index
    #                 # print ('NODE with stack top %s'%working_stack[-1])
    #                 if working_stack[-1-command.args[0]] in args:
    #                     # print ('*** %s %s %s'%(command,working_stack[-1-command.args[0]],args.index(working_stack[-1-command.args[0]])))
    #                     new_command,_ = self.create_command(NodeLabCmd(args.index(working_stack[-1-command.args[0]]), command.args[1]))
    #                     print ('*** %s %s'%(self.cmd_hash[new_command], args[self.cmd_hash[new_command].args[0]]))
    #                     updated_command_list.append(new_command)
    #                     del updated_list[inx]
    #                 else:
    #                     inx = inx + 1
    #             elif isinstance(command, EdgeLabCmd):
    #                 # TODO: rewrite
    #                 #print('%s'%working_stack)
    #                 #print ('*** %s %s %s'%(command,working_stack[-1-command.args[0]],working_stack[-1-command.args[2]]))
    #                 if working_stack[-1-command.args[0]] in args and working_stack[-1-command.args[2]] in args:
    #                     new_command, _ = self.create_command(EdgeLabCmd(args.index(working_stack[-1-command.args[0]]), command.args[1], args.index(working_stack[-1-command.args[2]])))
    #                     print ('**> %s %s %s'%(self.cmd_hash[new_command],args[self.cmd_hash[new_command].args[0]],args[self.cmd_hash[new_command].args[2]]))
    #                     updated_command_list.append(new_command)
    #                     del updated_list[inx]
    #                 else:
    #                     inx = inx + 1
    #             else:
    #                 inx = inx + 1

    #     return updated_command_list

    def find_scope(self, cmd_list: List[UUID]) -> Mapping[UUID,Tuple[int,int]]:
        """
        For each command in the list, finds the first and last index
        where
        """
        id_mapping: Mapping[UUID, Tuple[int, int]] = {}
        working_state: List[UUID] = []

        for inx, cmd in enumerate(cmd_list):
            cmd = self.cmd_hash[cmd]
            if isinstance(cmd, PushCmd):
                the_id = cmd.args[0]
                working_state.append(the_id)
                if the_id in id_mapping:
                    id_mapping[the_id] = (id_mapping[the_id][0], inx)
                else:
                    id_mapping[the_id] = (inx, inx)
            elif isinstance(cmd, NodeLabCmd):
                the_id = working_state[-1-cmd.args[0]]
            elif isinstance(cmd, EdgeLabCmd):
                the_id = working_state[-1-cmd.args[0]]
                if the_id in id_mapping:
                    id_mapping[the_id] = (id_mapping[the_id][0], inx)
                else:
                    id_mapping[the_id] = (inx, inx)
                the_id = working_state[-1-cmd.args[2]]
                if the_id in id_mapping:
                    id_mapping[the_id] = (id_mapping[the_id][0], inx)
                else:
                    id_mapping[the_id] = (inx, inx)

        return id_mapping

    def create_composite_from_ids(self, one: UUID, two: UUID) -> Tuple[UUID, int]:
        argsize = self.cmd_argsize[one] + self.cmd_argsize[two]
        new_command, _ = self.create_command(CatCmd(one, two), argsize)

        return (new_command, argsize) 

    def create_composite(self, cmd1: Cmd, cmd2: Cmd) -> Tuple[UUID, int]:
        argsize = self.cmd_argsize[cmd1.get_id()] + self.cmd_argsize[cmd2.get_id()]
        new_command, _ = self.create_command(CatCmd(cmd1.get_id(), cmd2.get_id()), argsize)

        return (new_command, argsize) 

    def reverse_indices(self, sequence):
        reversed = []
        working_state = []

        for item in sequence:
            cmd = self.cmd_hash[item]
            if isinstance(cmd, PushCmd):# and cmd.args[0] not in working_state:
                working_state.append(cmd.args[0])
                print("(%s)" %cmd)

            if isinstance(cmd, NodeLabCmd):
                print("%s -> " %cmd)
                arg = working_state[-cmd.args[0]-1]
                cmd.args[0] = len(working_state) - 1 - cmd.args[0]
                # self.create_command(cmd)
                print("--> %s " %cmd)
                if arg != working_state[cmd.args[0]]:
                    raise "Error"
            elif isinstance(cmd, EdgeLabCmd):
                print("%s -> " %cmd)
                arg = working_state[-cmd.args[0]-1]
                cmd.args[0] = len(working_state) - 1 - cmd.args[0]
                if arg != working_state[cmd.args[0]]:
                    raise "Error"
                arg = working_state[-cmd.args[2]-1]
                cmd.args[2] = len(working_state) - 1 - cmd.args[2]
                if arg != working_state[cmd.args[2]]:
                    raise "Error"
                print("--> %s " %cmd)
                # self.create_command(cmd)

            reversed.append(cmd)

        return reversed, working_state

    def create_subgraph_sets(self, window_size):
        """
        For each start/end index in the node window,
        find all nodes and edges belong to it.

        We see if we can find the same pattern
        across different subgraphs -- this is a motif
        """
        return

    def flush_working_sequence(self):
        # For now, dequeue all items in the working sequence
        # TODO: reorder, merge the PUSHes, add CONCAT and appropriate
        # re-indexing

        # self.working_sequence = self.merge_bindings(self.working_sequence)
        scope_map = self.find_scope(self.working_sequence)
        pop_map: Mapping[int, MutableSet[int]] = {}
        for key in scope_map:
            if scope_map[key][1] in pop_map:
                pop_map[scope_map[key][1]].add(key)
            else:
                pop_map[scope_map[key][1]] = set([key])

        sequence, allstate = self.reverse_indices(self.working_sequence)

        # print (sequence)

        # TODO: need to reindex positional indices as we pop items!

        # Sketch: convert all positions to ABSOLUTE indices
        # In last step convert them to RELATIVE indices

        print(allstate)

        new_seq = []
        working_state = []
        for inx, cmd in enumerate(sequence):
            print("> %s"%cmd)
            new_seq.append(cmd.get_id())
            #cmd = self.cmd_hash[item]
            if isinstance(cmd, PushCmd):# and cmd.args[0] not in working_state:
                working_state.append(cmd.args[0])
                print(working_state)
            if inx in pop_map:
                for it2 in pop_map[inx]:
                    cmd = self.create_command(PopCmd(it2))[0]
                    print("Pop %s"%self.cmd_hash[cmd])
                    new_seq.append(cmd)
                    del working_state[-1]

                # TODO: for all remaining nodes / edges, realign
                # stack
            if isinstance(cmd, NodeLabCmd):
                arg = allstate[cmd.args[0]]
                cmd.args[0] = len(working_state) - 1 - working_state.index(arg)
                c2,_ = self.create_command(cmd)
                new_seq.append(c2)
            elif isinstance(cmd, EdgeLabCmd):
                cmd.args[0] = len(working_state) - 1 - cmd.args[0]
                cmd.args[2] = len(working_state) - 1 - cmd.args[2]
                c2,_ = self.create_command(cmd)
                new_seq.append(c2)

        self.working_sequence.clear()
        self.working_sequence += new_seq

        # Trigger a CONCAT each time we have a new PUSH that doesn't 
        # match an existing sequence?
        last_item = None
        last_done = False
        done = set()
        for item in self.working_sequence:
            # if last_item and item in done and last_done:
            #     item, siz = self.create_composite_from_ids(last_item, item)
            #     self.cmd_log.remove(1)
            self.cmd_log.append(self.cmd_hash[item])
            last_done = item in done
            done.add(item)
            last_item = item

        self.working_sequence.clear()


    def add_node(self, id: UUID, label: str, values: Tuple[Any]) -> UUID:
        """
        Create a new node with a given id and tuple
        """

        if id in self.data_entries:
            inx = len(self.data_entries) - self.data_entries.index(id) - 1
        else:
            bind_cmd,_ = self.create_command(PushCmd([id,values]))
            self.add_or_promote_command(bind_cmd)
            self.working_sequence.append(bind_cmd)
            self.data_entries.append(id)
            inx = 0

        node_cmd,_ = self.create_command(NodeLabCmd(inx, label))
        self.add_or_promote_command(node_cmd)
        self.working_sequence.append(node_cmd)

        # self.flush_working_sequence()

        return node_cmd

    def add_edge(self, source: UUID, label: str, dest: UUID) -> UUID:
        """
        Adds an edge between the source and node with a given label.
        Current version does NOT have properties but this could be extended.
        """

        if source in self.data_entries:
            sinx = len(self.data_entries) - self.data_entries.index(source) - 1
        else:
            sinx = 0
            bind1_cmd,_ = self.create_command(PushCmd([dest]))
            self.add_or_promote_command(bind1_cmd)
            self.working_sequence.append(bind1_cmd)
        
        if dest in self.data_entries:
            dinx = len(self.data_entries) - self.data_entries.index(dest) - 1
        else:
            dinx = 0
            bind2_cmd,_ = self.create_command(PushCmd([source]))
            self.add_or_promote_command(bind2_cmd)
            self.working_sequence.append(bind2_cmd)

        edge_cmd,_ = self.create_command(EdgeLabCmd(sinx, label, dinx))
        self.add_or_promote_command(edge_cmd)
        self.working_sequence.append(edge_cmd)

        # self.flush_working_sequence()

        return edge_cmd

class ProvenanceScript(ProvenanceStore):
    """
    Adapter from ProvenanceStore to a graph script
    """
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
        print('Edge: (%s,%s,%s)' %(source,label,dest))
        self.script.add_edge(source, label, dest)
        return 1

    def add_nodeprop(self, db, resource, node, label, value, ind=None):
        # type: (cursor, str, str, str, Any, int) -> None
        return 1

    def flush(self, db, resource):
        self.script.flush_working_sequence()
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
    edge3 = store.add_edge(db, 'mprov', prog1_exec1, 'used', input_common)
    edge4 = store.add_edge(db, 'mprov', output1, 'wasGeneratedBy', prog1_exec1)
    edge5 = store.add_edge(db, 'mprov', prog1_exec1, 'used', prog1_source)
    edge6 = store.add_edge(db, 'mprov', output1, 'wasDerivedFrom', input1)
    edge7 = store.add_edge(db, 'mprov', output1, 'wasDerivedFrom', input2)
    edge8 = store.add_edge(db, 'mprov', output1, 'wasDerivedFrom', input_common)

def simple_test(db, store):
    # These nodes are used across multiple motifs
    input_common = store.add_node(db, "mprov", "entity", ('file1',))
    prog1_source = store.add_node(db, 'mprov', 'entity', ('prog1.c', '1-1-1980'))

    write_motif(db, store, prog1_source, input_common, 10)
    write_motif(db, store, prog1_source, input_common, 20)
    write_motif(db, store, prog1_source, input_common, 30)

    store.flush(db, "mprov")

simple_test(None, ProvenanceScript(ProvenanceStore()))