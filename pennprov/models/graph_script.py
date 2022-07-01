from enum import Enum
from typing import List, Any, Mapping
import uuid
from uuid import UUID

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

class Cmd:
    op = None            # type: Op
    args = None          # Type: List[None]

    def __init__(self, op, args):
        # type: (Op, List[Any]) -> None
        self.op = op
        self.args = args

class PushCmd(Cmd):
    def __init__(self, arg):
        # type: (UUID|str) -> None
        super.__init__(Op.PUSH, [arg])

class SetCmd(Cmd):
    def __init__(self, arg, pos):
        # type: (UUID|str, int) -> None
        super.__init__(Op.SET, [arg, pos])

class PopCmd(Cmd):
    def __init__(self):
        # type: () -> None
        super.__init__(Op.POP, [])

class DelCmd(Cmd):
    def __init__(self, pos):
        # type: (int) -> None
        super.__init__(Op.DEL, [pos])

class XchCmd(Cmd):
    def __init__(self, pos1, pos2):
        # type: (int, int) -> None
        super.__init__(Op.XCH, [pos1, pos2])

class NodeCmd(Cmd):
    def __init__(self, idinx, labinx):
        # type: (int, int) -> None
        super.__init__(Op.NODE, [idinx, labinx])

class NodeLabCmd(Cmd):
    def __init__(self, idinx, label):
        # type: (int, str) -> None
        super.__init__(Op.NODE_LAB, [idinx, label])

class EdgeCmd(Cmd):
    def __init__(self, frominx, labinx, toinx):
        # type: (int, int, int) -> None
        super.__init__(Op.EDGE, [frominx, labinx, toinx])

class EdgeLabCmd(Cmd):
    def __init__(self, frominx, label, toinx):
        # type: (int, str, int) -> None
        super.__init__(Op.EDGE_LAB, [frominx, label, toinx])

class GraphScript:
    # Bounded LRU queue
    cmd_list = []           # type: List[UUID]
    cmd_hash = []           # type: Mapping[UUID,Cmd]

    max = 1024

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
        id = GraphScript.get_id_from_key(cmd)
        self.cmd_list.append(id)
        if id not in self.cmd_hash:
            self.cmd_hash[id] = cmd

        self.evict()

        return id

    def reuse_command(self, inx_pos):
        pass

    def discard_command(self, inx_pos):
        pass


    def apply_script(self, target, start=0, end=-1):
        pass