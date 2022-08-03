######################
## mProv Copyright (C) 2017-22 by Trustees of the University of Pennsylvania
## All Rights Reserved.
## 
##
# ## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
######################

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

#sub_stream_1 = None
#sub_stream_2 = None
#mprov_conn.create_or_reset_graph()
# main_stream = mprov_conn.create_collection('output_ecg')
# sub_stream_1 = mprov_conn.create_collection('output_ecg_1', 1)
# sub_stream_2 = mprov_conn.create_collection('output_ecg_2', 1)
# mprov_conn.add_to_collection(sub_stream_1, main_stream)
# mprov_conn.add_to_collection(sub_stream_2, main_stream)

def x_test_main():
    global mprov_conn

    mprov_conn.create_or_reset_graph()
    main_stream = mprov_conn.create_collection('output_ecg')
    sub_stream_1 = mprov_conn.create_collection('output_ecg_1', 1)
    sub_stream_2 = mprov_conn.create_collection('output_ecg_2', 1)
    mprov_conn.add_to_collection(sub_stream_1, main_stream)
    mprov_conn.add_to_collection(sub_stream_2, main_stream)

    # Test the decorators, which will create entities for the dataframe
    # elements, and nodes representing the dataframe components
    ecg = pd.DataFrame([{'x':1, 'y': 2}, {'x':3, 'y':4}])
    tst(ecg)
    tstx(ecg)

    mprov_conn.store_annotations(sub_stream_1, {'name': 'ecg', 'date': '01-01-01'})
    mprov_conn.store_annotations(sub_stream_2, {'name': 'eeg', 'date': '01-01-05'})

    mprov_conn.flush()

    mprov_conn.get_dot("test_main.dot")

    df = ecg

    id = mprov_conn.get_token_qname(mprov_conn.get_entity_id('output_ecg', 'w[[1, 1], [3, 1]]'))
    node = mprov_conn.get_node(id)
    logging.info ("Output ECG node %s is %s" %(MProvConnection.get_local_part(id), node))

    # What are the sources for a given output ECG (these should be windows)
    source_list = mprov_conn.get_source_entities(mprov_conn.get_token_qname(mprov_conn.get_entity_id('output_ecg', 'w[[1, 1], [3, 1]]')))
    logging.info ("Sources: %s" %(str(source_list)))
    assert(len(source_list) == 1)
    # Are there any derived?
    derived_list = mprov_conn.get_derived_entities(mprov_conn.get_token_qname(mprov_conn.get_entity_id('output_ecg', 'w[[1, 1], [3, 1]]')))
    logging.info ("Should be no derived: %s" %str(derived_list))
    assert(len(derived_list) == 0)

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

    # the_producers = mprov_conn.get_stream_producers("output_ecg")

    # assert (len(the_producers) == 1)
    # assert ('def test' in the_producers[0])

    # logging.info (the_producers)

    ####  [i1] \
    ####  [i2] -- [w_{i1,i2,i3}] <-used- (f) <-wasGeneratedBy- [o123]
    ####  [i3] /
    ####

def test_at_scale():
    mprov_conn.create_or_reset_graph()
    main_stream = mprov_conn.create_collection('output_ecg')
    sub_stream_1 = mprov_conn.create_collection('output_ecg_1', 1)
    sub_stream_2 = mprov_conn.create_collection('output_ecg_2', 1)
    mprov_conn.add_to_collection(sub_stream_1, main_stream)
    mprov_conn.add_to_collection(sub_stream_2, main_stream)

    rows = []
    inx = 0
    start = datetime.now()
    for i in range(0, 1):
        for j in range(0, 10):
            rows = rows + [{'id': inx, 'x': i, 'y': j}]
            ecg = pd.DataFrame(rows)
            tst(ecg)
            tstx(ecg)
            inx = inx + 1

    mprov_conn.flush()

    mprov_conn.get_dot("test_at_scale.dot")
    print('Finished after %s' %(datetime.now()-start))

def test_graph_flat():
    #mprov_conn.create_or_reset_graph()
    start = datetime.now()
    a = mprov_conn.store_agent('A')

    b = mprov_conn.store_agent('B')
    mprov_conn.add_to_collection(a,b)
    c = mprov_conn.store_agent('C')
    mprov_conn.add_to_collection(a,c)

    for i in range(1,5):
        d = mprov_conn.store_agent('D')
        mprov_conn.add_to_collection(a,d)
        e = mprov_conn.store_activity('E',i,i+1)
        mprov_conn.add_to_collection(d,e)

def x_test_graph():
    #mprov_conn.create_or_reset_graph()
    start = datetime.now()
    a = mprov_conn.store_agent('A')
    b = mprov_conn.store_agent('B')
    mprov_conn.add_to_collection(a,b)
    c = mprov_conn.store_agent('C')
    mprov_conn.add_to_collection(b,c)
    d = mprov_conn.store_agent('D')
    mprov_conn.add_to_collection(c,d)
    e = mprov_conn.store_activity('E',1,2)
    mprov_conn.add_to_collection(c,e)
    mprov_conn.add_to_collection(d,e)

    if False:
        f = mprov_conn.store_agent('F')
        mprov_conn.add_to_collection(d,f)
        mprov_conn.add_to_collection(e,f)
        g = mprov_conn.store_agent('G')
        mprov_conn.add_to_collection(b,g)
        h = mprov_conn.store_agent('H')
        mprov_conn.add_to_collection(g,h)
        i = mprov_conn.store_agent('I')
        mprov_conn.add_to_collection(g,i)
        mprov_conn.add_to_collection(h,i)
        j = mprov_conn.store_agent('J')
        mprov_conn.add_to_collection(h,j)
        mprov_conn.add_to_collection(i,j)
        k = mprov_conn.store_agent('K')
        mprov_conn.add_to_collection(a,k)
        l = mprov_conn.store_agent('L')
        mprov_conn.add_to_collection(k,l)
        m = mprov_conn.store_agent('M')
        mprov_conn.add_to_collection(l,m)
        n = mprov_conn.store_agent('N')
        mprov_conn.add_to_collection(l,n)
        mprov_conn.add_to_collection(m,n)
        o = mprov_conn.store_agent('O')
        mprov_conn.add_to_collection(m,o)
        mprov_conn.add_to_collection(n,o)
        p = mprov_conn.store_agent('P')
        mprov_conn.add_to_collection(k,p)
        q = mprov_conn.store_agent('Q')
        mprov_conn.add_to_collection(p,q)
        r = mprov_conn.store_agent('R')
        mprov_conn.add_to_collection(p,r)
        mprov_conn.add_to_collection(q,r)
        s = mprov_conn.store_agent('S')
        mprov_conn.add_to_collection(q,s)
        mprov_conn.add_to_collection(r,s)
        t = mprov_conn.store_agent('T')
        mprov_conn.add_to_collection(f,t)
        mprov_conn.add_to_collection(j,t)
        u = mprov_conn.store_agent('U')
        mprov_conn.add_to_collection(o,u)
        mprov_conn.add_to_collection(s,u)
    mprov_conn.flush()

    mprov_conn.get_dot("test_graph.dot")
    print('Finished after %s' %(datetime.now()-start))

@MProvAgg("ecg", 'output_ecg',['x','y'],['x','y'], sub_stream_1)
def tst(n):
    return n.groupby('x').count()

@MProvAgg("ecg", 'output_ecg',['x'],['x'], sub_stream_2)
def tstx(n):
    return n.groupby('x').count()
