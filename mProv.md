# mProv API

mProv stores **provenance information** using the PROV-DM model.  This represents data and its associations with activities, agents (users), and other entities in a *graph*.

## Using the Manual API

Let's suppose we are running a stream computation through a pipeline of operators (eg in Apache Spark).

We can establish a connection to mProv by instantiating `MProvConnection`.

As we read a tuple from the stream, we want to:

1. Create a node in our PROV-DM graph representing that tuple.  This lets us capture annotations to the tuple, link activities to the tuple, etc.
   We are allowed to store **the whole tuple** (making the PROV structure self-contained) or **a link to the tuple, eg by its ID**, which then requires
   someone to look up the original tuple to get the data.  This is through `store_stream_tuple` (which takes a stream name and a unique ID, eg a 
   monotonic counter) and it returns a **token** or a node ID for the result.
2. We may want to **annotate** the tuple with "metadata", which in our case means key-value pairs that are stored in the provenance database but may not be 
   part of the dataflow in the stream engine.  This is through `store_annotations`, which lets us add a dictionary of key-value pairs to a stored node.
3. We may want to **operate** on the tuple `t` by applying some tuple-at-a-time function `f` (think of a "map" in MapReduce, or a user-defined predicate in SQL), producing `u`.  Here, we capture in the graph a node representing the **operation**.
   the time of the computation, the input, and the output.  This can be achieved via `store_derived_result`.
   
## More Advanced Features

**Aggregate or Windowed Computations.**  Sometimes we process data in **sliding0window** or **aggregate** computation `G` over a set or sequence of tuples `T` instead of one tuple at a time.  
In this case, we should store each tuple from `T` as in (1) above, then call `store_windowed_result` to associate the IDs of the tuples in `T` with a
collection, which are then processed by `G` resulting in a stream output result `u`.

**Annotating sub-streams, sources, or other collections.** At times, we have metadata that applies to an entire source and never changes, or that applies to
a sub-stream.  To represent this, we can create a *collection* representing the stream or sub-stream, annotate the collection, and associate each tuple
with the collection.  To do this, we provide `create_collection`, we allow the user to `store_annotations` on a collection, and we include `add_to_collection` 
to link a tuple to a collection.
