from pennprov.models.graph_script import GraphScript, ProvenanceScript, ProvenanceStore

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