import logging
from datetime import timezone, datetime
from functools import wraps

from pennprov import RelationModel
from pennprov.connection.mprov_connection import MProvConnection
from pennprov.connection.mprov_connection_cache import MProvConnectionCache
from pennprov.metadata.stream_metadata import BasicSchema, BasicTuple
import pandas as pd
import inspect

blank = BasicSchema({})
blank_tuple = BasicTuple(blank)

get_entity_id = MProvConnection.get_entity_id

stored = {}

def MProvAgg(in_stream_name,out_stream_name,in_stream_key=['index'],out_stream_key=['index'],collection=None,connection_key=None):
    """
    MProvAgg: decorator for an aggregation operation over windows.  Creates a provenance
    node for each output stream element and attaches it to the in_stream_keys for the inputs.

    :param in_stream_name: The name of the input stream schema
    :param out_stream_name: The name of the output stream schema
    :param in_stream_key: The key fields in the input stream
    :param out_stream_key: The key fields of the output stream
    :param collection: The name of the output stream collection, to which this result should be appended
    :param connection_key: Unique ID for reusing cached connection to MProv server
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

    def _write_collection_relationships(mprov_conn, sig, derived, source):
        mprov_conn.store_derived_from(derived, source)
        activity_token = mprov_conn.store_activity(sig, None, None, None)

        uses = RelationModel(
            type='USAGE', subject_id=activity_token, object_id=source, attributes=[])
        mprov_conn.cache.store_relation(resource=mprov_conn.get_graph(), body=uses, label='used')

        generates = RelationModel(
            type='GENERATION', subject_id=derived, object_id=activity_token, attributes=[])
        mprov_conn.cache.store_relation(resource=mprov_conn.get_graph(), body=generates, label='wasGeneratedBy')

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

            global stored

            if func.__name__ not in stored:
                d = (inspect.getsource(func))
                stored[func.__name__] = mprov_conn.store_code(d)
                logging.debug('Storing %s as %s:%s', func.__name__, stored[func.__name__], d)

            sig = stored[func.__name__]

            # Create a window with the appropriate keys
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
                try:
                    for t in rel_keys(arg, in_stream_key):
                        #print('Input: %s' %in_stream_name + str([t[k] for k in in_stream_key]))

                        # This ensures that the input tuples actually exist.  It needs to merge
                        # if the tuple is already there
                        tup = mprov_conn.store_stream_tuple(in_stream_name,
                                                            [t[k] for k in in_stream_key], blank_tuple)

                        # Ensure that the input tuples are also linked to the appropriate stream
                        if in_stream_name not in stored:
                            stream_part = mprov_conn.create_collection(in_stream_name)
                            stored[in_stream_name] = stream_part.local_part
                        else:
                            stream_part = mprov_conn.get_qname(stored[in_stream_name])
                        mprov_conn.add_to_collection(tup, stream_part)
                except:
                    pass
                #print (window_ids)
                result = mprov_conn.store_windowed_result(out_stream_name, 'w'+str(out_keys), blank_tuple,
                                                 window_ids, sig, ts, ts)
                if out_stream_name not in stored:
                    stream_part = mprov_conn.create_collection(out_stream_name)
                    stored[out_stream_name] = stream_part.local_part

                    # Add derivation to source input
                    _write_collection_relationships(mprov_conn, sig, stream_part, mprov_conn.get_qname(stored[in_stream_name]))
                else:
                    stream_part = mprov_conn.get_qname(stored[out_stream_name])
                mprov_conn.add_to_collection(result, stream_part)

                if collection:
                    mprov_conn.add_to_collection(result, collection)
            else:
                logging.warning("Output: %s.%s <(%s)- %s", out_stream_name, 'w'+str(out_keys), sig, str(window_ids))

            return val
        return wrapper
    return inner_function

#if __name__ == '__main__':

