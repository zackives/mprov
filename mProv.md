# mProv API

mProv stores **provenance information** using the PROV-DM model.  This represents data and its associations with activities, agents (users), and other entities in a *graph*.  The graph conforms to a spec called [PROV-DM](https://www.w3.org/TR/prov-dm/).

![example](images/prov-example.png)

The example above shows a screen capture of the Neo4J graph visualizer, for a provenance graph captured by mProv.  This
graph currently omits the agent (user), but shows:

* In the "diamond" shape on the left, we have a node at the top representing a *stream* or source.  This stream:
  * Has two member tuples (below, as the left and right points of the "diamond").
  * Has two annotations, in the upper left.  
* The two stream tuples are aggregated into a sliding window or collection node, which is the bottom of the diamond.  Note that in the general case, not all tuples from a stream will be in the window.
* A computation (represented with the brown node) uses the sliding window to generate an output (rightmost green node).
* We record that the output was derived from the input window.

The provenance graph can, in turn, be *queried* (using either the mProv API or Neo4J Cypher) to discover relationships.
For instance, we can determine which nodes were produced by a given function or activity; we can traverse the graph
to determine which source was used for a given output result; we can find all annotations transitively associated with
our input window (by tracing through the tuples, to the sources, to their annotations).

## mProv Programmatic API

Let's suppose we are running a stream computation through a pipeline of operators (eg in Apache Spark).
We can establish a connection to mProv by instantiating `MProvConnection`.  This constructor takes as input
a user ID and password, as well as a server.

## Basics: Tuples, Annotations, Activities and Outputs

As we read a tuple *t* from the stream, we want to:

1. Create a node *n_t* in our PROV-DM graph representing tuple *t*.  This lets us capture annotations to the tuple, link activities to the tuple, etc.
   We are allowed to store **the whole tuple** (making the PROV structure self-contained) or **a link to the tuple, eg by its ID**, which then requires
   someone to look up the original tuple to get the data.  This is through `store_stream_tuple` (which takes a stream name and a unique ID, eg a 
   monotonic counter) and it returns a **token** or a node ID for the result.
2. We may want to **annotate** the tuple with "metadata", which in our case means key-value pairs that are stored in the provenance database but may not be 
   part of the dataflow in the stream engine.  This is through `store_annotations`, which lets us add a dictionary of key-value pairs to a stored node.
3. We may want to **operate** on the tuple `t` by applying some tuple-at-a-time function `f` (think of a "map" in MapReduce, or a user-defined predicate in SQL), producing `u`.  Here, we capture in the graph a node representing the **operation**.
   the time of the computation, the input, and the output.  This can be achieved via `store_derived_result`.
   
## More Advanced Features: Collection-Valued Data

**Aggregate or Windowed Computations.**  Sometimes we process data in **sliding window** or **aggregate** computation `G` over a set or sequence of tuples `T` instead of one tuple at a time.  
In this case, we should store each tuple from `T` as in (1) above, then call `store_windowed_result` to associate the IDs of the tuples in `T` with a
collection, which are then processed by `G` resulting in a stream output result `u`.

**Annotating sub-streams, sources, or other collections.** At times, we have metadata that applies to an entire source and never changes, or that applies to
a sub-stream.  To represent this, we can create a *collection* representing the stream or sub-stream, annotate the collection, and associate each tuple
with the collection.  To do this, we provide `create_collection`, we allow the user to `store_annotations` on a collection, and we include `add_to_collection` 
to link a tuple to a collection.

**Directly recording relationships.** If the programmer wishes to record a link between existing nodes (e.g., that a collection
was derived from another collection), we provide a series of API calls for this: `store_derived_from`, `store_used`, `store_generated_by`. 

## mProv Querying

mProv also provides programmatic calls to query the provenance graph, given a node:

* `get_node` takes any node ID and returns the tuple contents associated with the node
* `get_code` takes any code definition string and stores it as an entity, then returns a unique ID
* `get_annotations` returns a dictionary of key-value annotations associated with the node
* `get_source_entities` takes an entity node and traces the `wasDerivedFrom` edge to find sources
* `get_derived_entities` takes an entity node and traces back on the `wasDerivedFrom` edge to find derived nodes
* `get_parent_entities` takes an entity node and traces the `hadMember` edge to find containing entities
* `get_child_entities` takes an entity node and traces back on the `hadMember` edge to find sub-entities
* `get_creating_activities` takes an entity node and traces the `wasGeneratedBy` edge to find producing activities
* `get_activity_outputs` takes a activity node and traces back on the `wasGeneratedBy` edge to find output activities
* `get_activity_inputs` takes an activity node and traces the `used` edge to find input nodes

## mProv and Apache Spark

mProv interfaces with Apache Spark, with a focus on instrumenting user-defined functions called through the `pandas_udf`
decorator.  Here, Spark does a GROUP BY on a set of tuples, then calls the UDF with a subset of tuples, collected in a
Pandas dataframe.  (This is done through Apache Arrow.)

Here, a given Spark computation may have many executors on many machines.  Each machine should use mProv's `decorator`
module and the `MProvAgg` decorator.  The decorator will instrument the Pandas UDF with additional code to record
the function invocation, its inputs, and its return values. 

**Connection Cache.** Each time Spark calls MProvAgg on the *same executor node*, we would like to reuse the `MProvConnection`.
The `MProvConnectionCache` allows us to do so.

**Decorator syntax**.
`@MProvAgg(`*input_stream*, *output_stream*, *input_unique_att*, *output_unique_att*, *parent_sub_stream*)

* `input_stream` is the name of the input stream or relation
* `output_stream` is the name of the output stream or relation
* `input_unique_att` and `output_unique_att` are used to determine a *unique key* for each element of the input and output streams, respectively.
A monotonic timestamp is often used.
* `parent_sub_stream` specifies the ID for a PROV-DM node representing the output stream.  Each stream output will be linked to this node
(via a `hasMember` edge).
 