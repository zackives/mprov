import logging
import pytest

from pennprov.connection.mprov import MProvConnection
from pennprov.api.decorators import MProvAgg

import pandas as pd

logging.basicConfig(level=logging.DEBUG)

def test_main(cached_mprov_conn):
    #type: (MProvConnection) -> None

    sub_stream_1 = cached_mprov_conn.create_collection('output_ecg_1', 1)
    sub_stream_2 = cached_mprov_conn.create_collection('output_ecg_2', 1)

    @MProvAgg("ecg", 'output_ecg',['x','y'],['x','y'], sub_stream_1)
    def test(n):
        return n.groupby('x').count()

    @MProvAgg("ecg", 'output_ecg',['x'],['x'], sub_stream_2)
    def testx(n):
        return n.groupby('x').count()

    # Test the decorators, which will create entities for the dataframe
    # elements, and nodes representing the dataframe components
    ecg = pd.DataFrame([{'x':1, 'y': 2}, {'x':3, 'y':4}])
    test(ecg)
    testx(ecg)

    cached_mprov_conn.store_annotations(sub_stream_1, {'name': 'ecg', 'date': '01-01-01'})
    cached_mprov_conn.store_annotations(sub_stream_2, {'name': 'eeg', 'date': '01-01-05'})

    cached_mprov_conn.flush()

    df = ecg

    id = cached_mprov_conn.get_token_qname(cached_mprov_conn.get_entity_id('output_ecg', 'w[[1, 1], [3, 1]]'))
    node = cached_mprov_conn.get_node(id)
    print ("Output ECG node %s is %s" %(MProvConnection.get_local_part(id), node))

    # What are the sources for a given output ECG (these should be windows)
    source_list = cached_mprov_conn.get_source_entities(cached_mprov_conn.get_token_qname(cached_mprov_conn.get_entity_id('output_ecg', 'w[[1, 1], [3, 1]]')))
    assert(len(source_list) == 1)
    print (str(source_list))
    # Are there any derived?
    derived_list = cached_mprov_conn.get_derived_entities(cached_mprov_conn.get_token_qname(cached_mprov_conn.get_entity_id('output_ecg', 'w[[1, 1], [3, 1]]')))
    assert(len(derived_list) == 0)
    print (str(derived_list))

    # Take a source (window) and see if we can read it
    source_node = cached_mprov_conn.get_node(source_list[0])
    print (str(source_node))
    assert (len(source_node) == 1)# and source_node[0]['type'] == 'QUALIFIED_NAME')
    # and trace to the input tuples
    tuples_list = cached_mprov_conn.get_child_entities(source_list[0])
    assert (len(tuples_list) == 2)
    print (str(tuples_list))

    activity = cached_mprov_conn.get_creating_activities(cached_mprov_conn.get_token_qname(cached_mprov_conn.get_entity_id('output_ecg', 'w[[1, 1], [3, 1]]')))
    print (str(activity))
    assert (len(activity) == 1)
    gen = cached_mprov_conn.get_activity_outputs(activity[0])
    assert (len(gen) == 1)
    print (str(gen))

    input_windows = cached_mprov_conn.get_activity_inputs(activity[0])
    assert (len(input_windows) == 1)
    assert (MProvConnection.get_local_part(input_windows[0]) == "output_ecg_w.w[[1, 1], [3, 1]]")
    print (str(input_windows))

    cached_mprov_conn.store_annotations(gen[0], {'first': 'value', 'second':0})

    cached_mprov_conn.flush()
    ann = cached_mprov_conn.get_annotations(gen[0])
    print ("Annotations on %s: %s" %(str(MProvConnection.get_local_part(gen[0])), str(ann)))
    assert (len(ann) == 2)

    assert (cached_mprov_conn.get_stream_inputs("output_ecg")[0] == "ecg")

    the_producers = cached_mprov_conn.get_stream_producers("output_ecg")

    assert (len(the_producers) == 1)
    assert ('def test' in the_producers[0])

    print (the_producers)

    ####  [i1] \
    ####  [i2] -- [w_{i1,i2,i3}] <-used- (f) <-wasGeneratedBy- [o123]
    ####  [i3] /
    ####