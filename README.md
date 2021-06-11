# pennprov

This Python package connects to the [PennProvenance](https://pennprovenance.net) provenance services, which are part of the broader Habitat Data Environment.  Additional high-level services oriented towards the mProv stream data provenance project are also included.

The main Python package is automatically generated by the [Swagger Codegen](https://github.com/swagger-api/swagger-codegen) project:

- API version: V1.1.2
- Package version: 2.2.11
- Build package: io.swagger.codegen.languages.PythonClientCodegen
For more information, please visit [https://bitbucket.org/penndb/hab-repo](https://bitbucket.org/penndb/hab-repo)

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

The PennProv packages connect to a REST-backed Web service, which in turn stores data in PostgreSQL and Neo4J.  If you are installing locally, you may wish to use our preconfigured Docker-Compose script.

```bash
cd docker-container
docker-compose up
```

Then (after waiting some time!) open your Web browser to http://localhost:8088 and click on `Sign up`.  

Create a new sample user called `YOUR_USERNAME` with password `YOUR_PASSWORD`.

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

## Documentation for API Endpoints

All URIs are relative to *http://localhost:8088*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AuthenticationApi* | [**add_credential**](docs/AuthenticationApi.md#add_credential) | **POST** /auth/services/{service}/user/{username} | Adds a service credential for the user
*AuthenticationApi* | [**add_group**](docs/AuthenticationApi.md#add_group) | **POST** /auth/organizations/{organization}/group/{group} | Adds a permissions group to an organization
*AuthenticationApi* | [**add_organization**](docs/AuthenticationApi.md#add_organization) | **POST** /auth/organizations/{orgname} | Adds an organization
*AuthenticationApi* | [**add_subgroup_to_group**](docs/AuthenticationApi.md#add_subgroup_to_group) | **POST** /auth/groups/{groupname}/group/{subgroup} | Adds a subgroup to a group
*AuthenticationApi* | [**add_user_to_group**](docs/AuthenticationApi.md#add_user_to_group) | **POST** /auth/groups/{groupname}/user/{username} | Adds a user to a group
*AuthenticationApi* | [**add_user_to_organization**](docs/AuthenticationApi.md#add_user_to_organization) | **POST** /auth/organizations/{orgId}/user/{username} | Adds a user to an organization
*AuthenticationApi* | [**create_new_user**](docs/AuthenticationApi.md#create_new_user) | **POST** /auth/credentials/{username} | Creates a new user
*AuthenticationApi* | [**get_group_from_id**](docs/AuthenticationApi.md#get_group_from_id) | **GET** /auth/groups/id/{groupId} | Gets a group name from its integer ID
*AuthenticationApi* | [**get_group_id**](docs/AuthenticationApi.md#get_group_id) | **GET** /auth/groups/name/{groupName} | Gets a group&#39;s ID from its name
*AuthenticationApi* | [**get_group_ids_for_user**](docs/AuthenticationApi.md#get_group_ids_for_user) | **GET** /auth/credentials/{username}/groups/id | Gets the IDs of groups in which a user is directly a member
*AuthenticationApi* | [**get_groups_for_user**](docs/AuthenticationApi.md#get_groups_for_user) | **GET** /auth/credentials/{username}/groups | Gets the groups in which a user is directly a member
*AuthenticationApi* | [**get_organization_from_id**](docs/AuthenticationApi.md#get_organization_from_id) | **GET** /auth/organizations/id/{orgId} | Gets an organization name from its integer ID
*AuthenticationApi* | [**get_organization_id**](docs/AuthenticationApi.md#get_organization_id) | **GET** /auth/organizations/name/{orgName} | Gets an organization ID from its name
*AuthenticationApi* | [**get_parent_group_ids**](docs/AuthenticationApi.md#get_parent_group_ids) | **GET** /auth/groups/id/{groupId}/parents/id | Gets the IDs of parent groups
*AuthenticationApi* | [**get_parent_groups**](docs/AuthenticationApi.md#get_parent_groups) | **GET** /auth/groups/name/{groupName}/parents/name | Gets the groups in which a user is directly a member
*AuthenticationApi* | [**get_token_route**](docs/AuthenticationApi.md#get_token_route) | **POST** /auth/tokens/{username} | Requests a new token
*AuthenticationApi* | [**get_user_info**](docs/AuthenticationApi.md#get_user_info) | **GET** /auth/credentials/{username}/info | Gets a user&#39;s info
*AuthenticationApi* | [**is_registered**](docs/AuthenticationApi.md#is_registered) | **GET** /auth/services/{service}/user/{username} | Returns whether a user credential is valid for a service
*AuthenticationApi* | [**is_valid_credential**](docs/AuthenticationApi.md#is_valid_credential) | **POST** /auth/services/local/user/{username}/credential | Returns whether a local user credential is valid
*AuthenticationApi* | [**update_user**](docs/AuthenticationApi.md#update_user) | **PUT** /auth/credentials/{username} | Updates user properties
*PermissionApi* | [**add_permission**](docs/PermissionApi.md#add_permission) | **POST** /perms/types/{permname} | Adds a new labeled permission type
*PermissionApi* | [**get_group_permissions_on**](docs/PermissionApi.md#get_group_permissions_on) | **GET** /perms/objects/{object}/group/{groupName} | Gets the group&#39;s permissions on an object
*PermissionApi* | [**get_object_ids**](docs/PermissionApi.md#get_object_ids) | **GET** /perms/name/{permname}/user/{username} | Gets the object ids for which the user has the given permission
*PermissionApi* | [**get_permission_from_id**](docs/PermissionApi.md#get_permission_from_id) | **GET** /perms/id/{id}/name | Gets a permission&#39;s name from its integer ID
*PermissionApi* | [**get_permission_id**](docs/PermissionApi.md#get_permission_id) | **GET** /perms/name/{name}/id | Gets a permission&#39;s ID from its name
*PermissionApi* | [**get_user_permissions_on**](docs/PermissionApi.md#get_user_permissions_on) | **GET** /perms/objects/{object}/user/{username} | Gets the user&#39;s permissions on an object
*PermissionApi* | [**grant_group_permission_on**](docs/PermissionApi.md#grant_group_permission_on) | **POST** /perms/objects/{object}/group/{groupName}/{permname} | Grants a group a permission on an object
*PermissionApi* | [**grant_user_permission_on**](docs/PermissionApi.md#grant_user_permission_on) | **POST** /perms/objects/{object}/user/{username}/{permname} | Grants a user a permission on an object
*PermissionApi* | [**revoke_group_permission_on**](docs/PermissionApi.md#revoke_group_permission_on) | **DELETE** /perms/objects/{object}/group/{groupName}/{permname} | Revokes a group a permission on an object
*PermissionApi* | [**revoke_user_permission_on**](docs/PermissionApi.md#revoke_user_permission_on) | **DELETE** /perms/objects/{object}/user/{username}/{permname} | Revokes a user a permission on an object

## Documentation For Authorization


## jwt

- **Type**: API key
- **API key parameter name**: api_key
- **Location**: HTTP header

