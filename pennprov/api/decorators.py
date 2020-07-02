import collections
import inspect
import logging
from datetime import timezone, datetime
from functools import wraps
import os
from pennprov.connection.mprov_connection import MProvConnection
from pennprov.connection.mprov_connection_cache import MProvConnectionCache
from pennprov.metadata.stream_metadata import BasicSchema, BasicTuple
import pandas as pd


blank = BasicSchema({})
blank_tuple = BasicTuple(blank)

get_entity_id = MProvConnection.get_entity_id

def MProvAgg(in_stream_name,op,out_stream_name,in_stream_key=['index'],out_stream_key=['index'],collection=None,map=None,connection_key=None):
    """
    MProvAgg: decorator for an aggregation operation over windows.  Creates a provenance
    node for each output stream element and attaches it to the in_stream_keys for the inputs.

    :param in_stream_name: The name of the input stream schema
    :param out_stream_name: The name of the output stream schema
    :param in_stream_key: The key fields in the input stream
    :param out_stream_key: The key fields of the output stream
    :return:
    """
    def md_key(stream, key_list):
        if isinstance(stream, tuple) and len(stream) == 1:
            stream = stream[0]
        # If the stream is a dataframe, return the subset matching the key
        if isinstance(stream, pd.DataFrame):
            if not in_stream_key:
                return stream
            else:
                return str(stream.reset_index()[key_list])
        else:
            return repr(stream)

    def rel_keys(stream, key_list):
        if isinstance(stream, tuple) and len(stream) == 1:
            stream = stream[0]
        # If the stream is a dataframe, return the subset matching the key
        if isinstance(stream, pd.DataFrame):
            if not in_stream_key:
                return stream
            else:
                return stream.reset_index()[key_list].to_dict('records')
        else:
            return repr(stream)

    def inner_function(func):
        @wraps(func)
        def wrapper(arg):
            #args_repr = [md_key(a, in_stream_key) for a in args]
            #kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            #signature = ", ".join(args_repr + kwargs_repr)
            #print(f"Calling {func.__name__}({signature})")
            val = func(arg)#*args, **kwargs)

            key = connection_key or MProvConnectionCache.Key()
            mprov_conn = MProvConnectionCache.get_connection(key)

            window_ids = []
            for t in rel_keys(arg, in_stream_key):
                if mprov_conn:
                    window_ids.append(get_entity_id(in_stream_name, [t[k] for k in in_stream_key]))
                else:
                    window_ids.append(get_entity_id(in_stream_name, [t[k] for k in in_stream_key]))

            if isinstance(out_stream_key,list):
                if len(out_stream_key) == 1:
                    out_keys = val.reset_index()[out_stream_key[0]].to_list()
                else:
                    out_keys = []
                    # print(val.reset_index()[out_stream_key])
                    for tup in val.reset_index()[out_stream_key].iterrows():
                        out_keys.append(tup[1].to_list())
            else:
                out_keys = val.reset_index()[out_stream_key].to_list()

            ts = datetime.now(timezone.utc)
            if mprov_conn:
                #try:
                for t in rel_keys(arg, in_stream_key):
                    #print('Input: %s' %in_stream_name + str([t[k] for k in in_stream_key]))
                    tup = mprov_conn.store_stream_tuple(in_stream_name, [t[k] for k in in_stream_key], blank_tuple)
                    if collection:
                        mprov_conn.add_to_collection(tup, collection)
                #except:
                #    pass
                #print (window_ids)
                mprov_conn.store_windowed_result(out_stream_name, 'w'+str(out_keys), blank_tuple,
                                                 window_ids, op, ts, ts)
            else:
                logging.warning("Output: %s.%s <(%s)- %s", out_stream_name, 'w'+str(out_keys), op, str(window_ids))

            return val
        return wrapper
    return inner_function

if __name__ == '__main__':

    import pandas as pd
    logging.basicConfig(level=logging.DEBUG)
    connection_key = MProvConnectionCache.Key()
    mprov_conn = MProvConnectionCache.get_connection(connection_key)
    if mprov_conn:
        mprov_conn.create_or_reuse_graph()

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

####  [i1] \
####  [i2] -- [w_{i1,i2,i3}] <-used- (f) <-wasGeneratedBy- [o123]
####  [i3] /
####