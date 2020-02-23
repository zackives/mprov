import collections
import inspect
import logging
from datetime import timezone, datetime
from functools import wraps
import os
from pyspark import broadcast
from pennprov.connection.mprov_connection import MProvConnection
from pennprov.metadata.stream_metadata import BasicSchema, BasicTuple
import pandas as pd

# Try environment variables first
try:
    mprov_user = os.environ['MPROV_USER']
    mprov_password = os.environ['MPROV_PASSWORD']
    mprov_host = os.environ['MPROV_HOST']
    mprov_conn = None
except KeyError:
    # Try simple defaults second
    try:
        mprov_user = 'YOUR_USERNAME'
        mprov_password = 'YOUR_PASSWORD'
        mprov_conn = None
    except KeyError:
        mprov_conn = None


def get_entity_id(stream, id):
    # type: (str, Any) -> str
    return stream + '._e' + str(id)

blank = BasicSchema({})
blank_tuple = BasicTuple(blank)

def MProvAgg(in_stream_name,op,out_stream_name,in_stream_key=['index'],out_stream_key=['index'],map=None):
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

            mprov_conn = MProvConnection(mprov_user, mprov_password, mprov_host)

            window_ids = []
            for t in rel_keys(arg, in_stream_key):
                if mprov_conn:
                    window_ids.append(mprov_conn.get_entity_id(in_stream_name, [t[k] for k in in_stream_key]))
                else:
                    window_ids.append(get_entity_id(in_stream_name, [t[k] for k in in_stream_key]))

            if isinstance(out_stream_key,list):
                if len(out_stream_key) == 1:
                    out_keys = val.reset_index()[out_stream_key[0]].to_list()
                else:
                    out_keys = []
                    print(val.reset_index()[out_stream_key])
                    for tup in val.reset_index()[out_stream_key].iterrows():
                        out_keys.append(tup[1].to_list())
            else:
                out_keys = val.reset_index()[out_stream_key].to_list()

            ts = datetime.now(timezone.utc)
            if mprov_conn:
                #try:
                for t in rel_keys(arg, in_stream_key):
                    print('Input: %s' %in_stream_name + str([t[k] for k in in_stream_key]))
                    mprov_conn.store_stream_tuple(in_stream_name, [t[k] for k in in_stream_key], blank_tuple)
                #except:
                #    pass
                print (window_ids)
                mprov_conn.store_windowed_result(out_stream_name, 'w'+str(out_keys), blank_tuple,
                                                 window_ids, op, ts, ts)
                logging.warning("Output: %s.%s <(%s)- %s", out_stream_name, 'w' + str(out_keys), op, str(window_ids))
            else:
                logging.warning("Output: %s.%s <(%s)- %s", out_stream_name, 'w'+str(out_keys), op, str(window_ids))

            return val
        return wrapper
    return inner_function

@MProvAgg("ecg", 'test', 'output_ecg',['x','y'],['x','y'])
def test(n):
    return n.groupby('x').count()

@MProvAgg("ecg", 'test', 'output_ecg',['x'],['x'])
def testx(n):
    return n.groupby('x').count()

import pandas as pd

data = pd.DataFrame([{'x':1, 'y': 2}, {'x':3, 'y':4}])
test(data)
testx(data)

df = data

####  [i1] \
####  [i2] -- [w_{i1,i2,i3}] -used-> (f) -generates-> [o123]
####  [i3] /
####