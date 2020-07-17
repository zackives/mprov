import logging

from pennprov.connection.mprov_connection_cache import MProvConnectionCache
from pennprov.api.decorators import MProvAgg

import pandas as pd

logging.basicConfig(level=logging.DEBUG)
connection_key = MProvConnectionCache.Key()
mprov_conn = MProvConnectionCache.get_connection(connection_key)
if mprov_conn:
    mprov_conn.create_or_reset_graph()

sub_stream_1 = mprov_conn.create_collection('sub_stream_1', 1)
sub_stream_2 = mprov_conn.create_collection('sub_stream_2', 1)

@MProvAgg("ecg", 'test', 'output_ecg',['x','y'],['x','y'], sub_stream_1)
def test(n):
    return n.groupby('x').count()

@MProvAgg("ecg", 'test', 'output_ecg',['x'],['x'], sub_stream_2)
def testx(n):
    return n.groupby('x').count()

# Test the decorators, which will create entities for the dataframe
# elements, and nodes representing the dataframe components
data = pd.DataFrame([{'x':1, 'y': 2}, {'x':3, 'y':4}])
test(data)
testx(data)

mprov_conn.store_annotations(sub_stream_1, {'name': 'ecg', 'date': '01-01-01'})
mprov_conn.store_annotations(sub_stream_2, {'name': 'eeg', 'date': '01-01-05'})

df = data

node = mprov_conn.get_node(mprov_conn.get_token_qname(mprov_conn.get_entity_id('output_ecg', 'w[[1, 1], [3, 1]]')))
print (node)

# What are the sources for a given output ECG (these should be windows)
source_list = mprov_conn.get_source_entities(mprov_conn.get_token_qname(mprov_conn.get_entity_id('output_ecg', 'w[[1, 1], [3, 1]]')))
print (str(source_list))
# Are there any derived?
derived_list = mprov_conn.get_derived_entities(mprov_conn.get_token_qname(mprov_conn.get_entity_id('output_ecg', 'w[[1, 1], [3, 1]]')))
print (str(derived_list))

# Take a source (window) and see if we can read it
source_node = mprov_conn.get_node(source_list[0])
print (str(source_node))
# and trace to the input tuples
tuples_list = mprov_conn.get_child_entities(source_list[0])
print (str(tuples_list))

activity = mprov_conn.get_creating_activities(mprov_conn.get_token_qname(mprov_conn.get_entity_id('output_ecg', 'w[[1, 1], [3, 1]]')))
print (str(activity))
gen = mprov_conn.get_activity_outputs(activity[0])
print (str(gen))

input_windows = mprov_conn.get_activity_inputs(activity[0])
print (str(input_windows))

mprov_conn.store_annotations(gen[0], {'first': 'value', 'second':0})

print (str(mprov_conn.get_annotations(gen[0])))

####  [i1] \
####  [i2] -- [w_{i1,i2,i3}] <-used- (f) <-wasGeneratedBy- [o123]
####  [i3] /
####