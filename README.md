# mprov

This Python package is a fork of the [PennProvenance](https://pennprovenance.net) provenance services, which are part of the broader Penn Data Habitat Environment.  Project development was funded by NSF grant 1650813.

## Purpose

The PennProvenance framework is focused on providing **fine-grained provenance**; the mProv project further develops this to support **data stream provenance**.

We adopt the PROV-DM model, which in essence creates a *graph* while computation is ongoing.  We decide on a level of granularity for our operations (somewhere between full programs and machine-level instructions) and for our data (somewhere between full files and bytes).

* As we read an input data object, we store it (or a link to it) within the **provenance store**.  It becomes an **entity** in our graph.
* As we write an output data object, we should also capture what operation produced the object, and what the parameters and inputs were.  The operation is generally considered an **activity**, it *used* the input **entity**s, and it produced output **entity**s.

Each entity is typically given a unique name based on a set of **keys** or a sequence number.  Each activity is possibly linked to its source code (which is itself an **entity**) or is given a name that is a digest of the source; and is annotated with the **start** and **end** timestamps under which it ran.

## Requirements.

Python 2.7 and 3.4+; Docker and Docker Compose, if setting up the server in a Docker container.

## Installation & Usage

There are two main aspects to setup.

### pip install

Most likely you'll want to install the Python package with pip:

```sh
pip install pennprov
```
(you may need to run `pip` with root permission: `sudo pip install pennprov`.  If you are running from Jupyter Notebook, you will need to use `!pip install pennprov`.)

Then import the package:
```python
import pennprov 
```

### Getting Started - Docker

The PennProv packages connect to a REST-backed Web service, which in turn stores data in PostgreSQL.  If you are installing locally, you may wish to use our preconfigured Docker-Compose script.

```bash
cd docker-container
docker-compose up
```

## Getting Started - mProv Client

More detailed information is available in the [mProv API overview](mProv.md).  Here's a brief example using `MProvConnection`.

```
from pennprov.connection.mprov import MProvConnection
from pennprov.metadata.stream_metadata import BasicSchema, BasicTuple
from datetime import datetime, timezone

def area_circle(input):
    return {'key': input['key'],
        'value': input['value'] * input['value'] * 3.1415}

# Use host.docker.internal instead of localhost if you are running
# in a docker container
conn = MProvConnection('YOUR_USERNAME', 'YOUR_PASSWORD', 'http://localhost:8088')
conn.create_or_reset_graph()

# Create a simple relation or stream, with a binary schema
data_schema = BasicSchema('SampleStream', {'key': 'int', 'value': 'int'})
# Create a sample tuple
tuple = BasicTuple(data_schema, {'key': 1, 'value': 456})

# Store the initial data, get the ID (token) of its node in the graph
input_token = conn.store_stream_tuple('SampleStream', tuple['key'], tuple)

# Compute an operation over the tuple, convert it to a tuple
ts = datetime.now(timezone.utc)
result = area_circle(tuple)
# Rather than BasicTuple, which has a schema, you may also use a dict
out_tuple = BasicTuple(data_schema, result)

# Store the derived tuple and the derivation name / time
conn.store_derived_result('OutStream', out_tuple['key'], out_tuple, input_token, 'area_circle', ts, ts)

```

We have also included `Jupyter-PennProv.ipynb`, which is a Jupyter Notebook suitable for running in a Dockerized Jupyter (e.g., `all-spark-notebook`) that will connect to PennProvenance.
