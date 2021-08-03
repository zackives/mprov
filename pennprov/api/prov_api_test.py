import logging
import pytest

from datetime import datetime

from pennprov.connection.mprov import MProvConnection
from pennprov.connection.mprov_connection_cache import MProvConnectionCache
from pennprov.api.decorators import MProvAgg

import pandas as pd

logging.basicConfig(level=logging.DEBUG)
connection_key = MProvConnectionCache.Key()
mprov_conn = MProvConnectionCache.get_connection(connection_key)
if mprov_conn:
    mprov_conn.create_or_reset_graph()
else:
    raise RuntimeError('Could not connect')

sub_stream_1 = mprov_conn.create_collection('output_ecg_1', 1)
sub_stream_2 = mprov_conn.create_collection('output_ecg_2', 1)

@MProvAgg("ecg", 'output_ecg',['x','y'],['x','y'], sub_stream_1)
@pytest.mark.skip(reason="Not a test fn")
def test(n):
    return n.groupby('x').count()

@MProvAgg("ecg", 'output_ecg',['x'],['x'], sub_stream_2)
@pytest.mark.skip(reason="Not a test fn")
def testx(n):
    return n.groupby('x').count()

def test_main():
    mprov_conn.create_or_reset_graph()
    # Test the decorators, which will create entities for the dataframe
    # elements, and nodes representing the dataframe components
    ecg = pd.DataFrame([{'x':1, 'y': 2}, {'x':3, 'y':4}])
    test(ecg)
    testx(ecg)

    mprov_conn.store_annotations(sub_stream_1, {'name': 'ecg', 'date': '01-01-01'})
    mprov_conn.store_annotations(sub_stream_2, {'name': 'eeg', 'date': '01-01-05'})

    mprov_conn.flush()

    df = ecg

    id = mprov_conn.get_token_qname(mprov_conn.get_entity_id('output_ecg', 'w[[1, 1], [3, 1]]'))
    node = mprov_conn.get_node(id)
    logging.info ("Output ECG node %s is %s" %(MProvConnection.get_local_part(id), node))

    # What are the sources for a given output ECG (these should be windows)
    source_list = mprov_conn.get_source_entities(mprov_conn.get_token_qname(mprov_conn.get_entity_id('output_ecg', 'w[[1, 1], [3, 1]]')))
    assert(len(source_list) == 1)
    logging.info (str(source_list))
    # Are there any derived?
    derived_list = mprov_conn.get_derived_entities(mprov_conn.get_token_qname(mprov_conn.get_entity_id('output_ecg', 'w[[1, 1], [3, 1]]')))
    assert(len(derived_list) == 0)
    logging.info (str(derived_list))

    # Take a source (window) and see if we can read it
    source_node = mprov_conn.get_node(source_list[0])
    logging.info (str(source_node))
    assert (len(source_node) == 1)# and source_node[0]['type'] == 'QUALIFIED_NAME')
    # and trace to the input tuples
    tuples_list = mprov_conn.get_child_entities(source_list[0])
    assert (len(tuples_list) == 2)
    logging.info (str(tuples_list))

    activity = mprov_conn.get_creating_activities(mprov_conn.get_token_qname(mprov_conn.get_entity_id('output_ecg', 'w[[1, 1], [3, 1]]')))
    logging.info (str(activity))
    assert (len(activity) == 1)
    gen = mprov_conn.get_activity_outputs(activity[0])
    assert (len(gen) == 1)
    logging.info (str(gen))

    input_windows = mprov_conn.get_activity_inputs(activity[0])
    assert (len(input_windows) == 1)
    assert (MProvConnection.get_local_part(input_windows[0]) == "output_ecg_w.w[[1, 1], [3, 1]]")
    logging.info (str(input_windows))

    mprov_conn.store_annotations(gen[0], {'first': 'value', 'second':0})

    mprov_conn.flush()
    ann = mprov_conn.get_annotations(gen[0])
    logging.info ("Annotations on %s: %s" %(str(MProvConnection.get_local_part(gen[0])), str(ann)))
    assert (len(ann) == 2)

    assert (mprov_conn.get_stream_inputs("output_ecg")[0] == "ecg")

    the_producers = mprov_conn.get_stream_producers("output_ecg")

    assert (len(the_producers) == 1)
    assert ('def test' in the_producers[0])

    # logging.info (the_producers)

    ####  [i1] \
    ####  [i2] -- [w_{i1,i2,i3}] <-used- (f) <-wasGeneratedBy- [o123]
    ####  [i3] /
    ####

def test_at_scale():
    mprov_conn.create_or_reset_graph()
    rows = []
    inx = 0
    start = datetime.now()
    for i in range(0, 100):
        for j in range(0, 10):
            rows = rows + [{'id': inx, 'x': i, 'y': j}]
            ecg = pd.DataFrame(rows)
            test(ecg)
            testx(ecg)
            inx = inx + 1

    mprov_conn.flush()
    print('Finished after %s' %(datetime.now()-start))

