import logging
import sys
import traceback
from datetime import timezone, datetime
from functools import partial, wraps

from pennprov.connection.mprov import MProvConnection
from pennprov.connection.mprov_connection_cache import MProvConnectionCache
from pennprov.metadata.stream_metadata import BasicSchema, BasicTuple
import pandas as pd
import inspect

blank = BasicSchema({})
blank_tuple = BasicTuple(blank)

get_entity_id = MProvConnection.get_entity_id

stored = {}
class MProvAgg:
    def __init__(self, in_stream_name,out_stream_name,in_stream_key=['index'],out_stream_key=['index'],collection=None,connection_key=None):
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
        self.in_stream_name = in_stream_name
        self.out_stream_name = out_stream_name
        self.in_stream_key = in_stream_key
        self.out_stream_key = out_stream_key
        self.collection = collection
        self.connection_key = connection_key or MProvConnectionCache.Key()

        # For Spark. Flush anything created on the driver node prior to computation.
        mprov_conn = MProvConnectionCache.get_connection(self.connection_key);
        if mprov_conn:
            mprov_conn.flush()

    def md_key(self, stream, key_list):
        if isinstance(stream, tuple) and len(stream) == 1:
            stream = stream[0]
        # If the stream is a dataframe, return the subset matching the key
        if isinstance(stream, pd.DataFrame):
            if not self.in_stream_key:
                return stream
            else:
                return str(stream.reset_index()[key_list])
        else:
            return repr(stream)

    def rel_keys(self, stream, key_list):
        if isinstance(stream, tuple) and len(stream) == 1:
            stream = stream[0]
        # If the stream is a dataframe, return the subset matching the key
        if isinstance(stream, pd.DataFrame):
            if not self.in_stream_key:
                return stream
            else:
                return stream.reset_index()[key_list].to_dict('records')
        else:
            return repr(stream)

    @staticmethod
    def _write_collection_relationships(mprov_conn, sig, derived, source):
        mprov_conn.store_derived_from(derived, source)
        activity_token = mprov_conn.store_activity(sig, None, None, None)

        mprov_conn.store_used(activity_token, source)
        mprov_conn.store_generated_by(derived, activity_token)

    def __call__(self, func):
        global stored
        # Need this to happen here (decoration-time and not call-time)
        # while the source file is still available to Spark.
        if func.__name__ not in stored:
            d = (inspect.getsource(func))
            logging.debug('Read source of %s as %s', func.__name__, d)

        # pandas_udf with function type GROUPED_MAP have either one arg: (data), or two (key, data)
        args_count = len(inspect.getfullargspec(func)[0])

        @wraps(func)
        def wrapper(key, data):
            #args_repr = [md_key(a, in_stream_key) for a in args]
            #kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            #signature = ", ".join(args_repr + kwargs_repr)
            #print(f"Calling {func.__name__}({signature})")
            
            val = func(key, data) if args_count > 1 else func(data)

            mprov_conn = MProvConnectionCache.get_connection(self.connection_key)

            global stored

            stored[func.__name__] = mprov_conn.store_code(d)
            logging.debug('Storing %s as %s:%s', func.__name__, stored[func.__name__], d)
            sig = stored[func.__name__]




            # Create a window with the appropriate keys
            window_ids = []
            #for t in self.rel_keys(arg, self.in_stream_key):
            #    window_ids.append(get_entity_id(self.in_stream_name, [t[k] for k in self.in_stream_key]))

            if isinstance(self.out_stream_key,list):
                if len(self.out_stream_key) == 1:
                    out_keys = val.reset_index()[self.out_stream_key[0]].to_list()
                else:
                    out_keys = []
                    # print(val.reset_index()[out_stream_key])
                    for tup in val.reset_index()[self.out_stream_key].iterrows():
                        out_keys.append(tup[1].to_list())
            else:
                out_keys = val.reset_index()[self.out_stream_key].to_list()

            ts = datetime.now(timezone.utc)
            if mprov_conn:
                try:
                    for t in self.rel_keys(data, self.in_stream_key):
                        #print('Input: %s' %self.in_stream_name + str([t[k] for k in self.in_stream_key]))
                        window_ids.append(get_entity_id(self.in_stream_name, [t[k] for k in self.in_stream_key]))

                        # This ensures that the input tuples actually exist.  It needs to merge
                        # if the tuple is already there
                        tup = mprov_conn.store_stream_tuple(self.in_stream_name,
                                                            [t[k] for k in self.in_stream_key], blank_tuple)

                        # Ensure that the input tuples are also linked to the appropriate stream
                        if self.in_stream_name not in stored:
                            stream_part = mprov_conn.create_collection(self.in_stream_name)
                            stored[self.in_stream_name] = MProvConnection.get_local_part(stream_part)
                        else:
                            stream_part = mprov_conn.get_token_qname(stored[self.in_stream_name])
                        mprov_conn.add_to_collection(tup, stream_part)
                except:
                    print('Error')
                    print(sys.exc_info()[0])
                    traceback.print_exc()
                    pass
                #print (window_ids)
                result = mprov_conn.store_windowed_result(self.out_stream_name, 'w'+str(out_keys), blank_tuple,
                                                 window_ids, sig, ts, ts)
                if self.out_stream_name not in stored:
                    stream_part = mprov_conn.create_collection(self.out_stream_name)
                    stored[self.out_stream_name] = MProvConnection.get_local_part(stream_part)

                    # Add derivation to source input
                    self._write_collection_relationships(mprov_conn, sig, stream_part, mprov_conn.get_token_qname(stored[self.in_stream_name]))
                else:
                    stream_part = mprov_conn.get_token_qname(stored[self.out_stream_name])
                mprov_conn.add_to_collection(result, stream_part)

                if self.collection:
                    mprov_conn.add_to_collection(result, self.collection)
            else:
                logging.warning("Output: %s.%s <(%s)- %s", self.out_stream_name, 'w'+str(out_keys), sig, str(window_ids))

            return val
        return wrapper if args_count > 1 else partial(wrapper, None)

#if __name__ == '__main__':

