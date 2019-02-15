# pennprov
Habitat API

This Python package is automatically generated by the [Swagger Codegen](https://github.com/swagger-api/swagger-codegen) project:

- API version: V1.1.0
- Package version: 2.2.0
- Build package: io.swagger.codegen.languages.PythonClientCodegen
For more information, please visit [https://bitbucket.org/penndb/hab-repo](https://bitbucket.org/penndb/hab-repo)

## Requirements.

Python 2.7 and 3.4+; Docker and Docker Compose, if setting up the server in a Docker container.

## Installation & Usage
### pip install

You can install with pip

```sh
pip install pennprov
```
(you may need to run `pip` with root permission: `sudo pip install pennprov`)

Then import the package:
```python
import pennprov 
```

## Getting Started - Client

The following illustrates a simple use of the API to obtain a authentication token and then store and retrieve nodes and edges.

```python
"""Example usage of pennprov client"""

from __future__ import print_function
from pprint import pprint

import pennprov
from pennprov.rest import ApiException


def main():
    """Get a token and store a node"""
    # create instances of the API classes
    configuration = pennprov.configuration.Configuration()
    configuration.host = "http://localhost:8088"
    api_client = pennprov.ApiClient(configuration)    
    auth_api = pennprov.AuthenticationApi(api_client)
    prov_api = pennprov.ProvenanceApi(api_client)
    prov_dm_api = pennprov.ProvDmApi(api_client)
    username = "YOUR_USERNAME"
    credentials = pennprov.UserCredentials(
        "YOUR_PASSWORD")
    graph_name = "my_graph"

    try:
        # One-time initialization of client with a JWT token for
        # authentication.
        web_token = auth_api.get_token_route(username, credentials)
        token = web_token.token
        print("Setting token %s\n" % token)
        configuration.api_key["api_key"] = token

        # Once api_key is set we can call services. For example,
        # store_prov_node
        prov_token_value = "my_prov_token"
        stream = pennprov.IDModel("my_stream.0")
        prov_location = pennprov.ProvLocationModel(
            stream=stream,
            field="my_source",
            position=[1, 2])
        data = [pennprov.FieldModel(
            name="my_boolean_field", type="BOOLEAN", value="true")]
        tuple_with_schema = pennprov.TupleWithSchemaModel(
            schema_name="my_schema", tuple=data, lookup_keys=[])
        body = pennprov.StoreNodeModel(
            prov_specifier=prov_location, tuple_with_schema=tuple_with_schema)
        prov_api.create_provenance_graph(graph_name)
        prov_api.store_provenance_node(graph_name, prov_token_value, body)

        # Retrieve the data from the node
        response = prov_api.get_provenance_data(graph_name, prov_token_value)
        pprint(response)

        # We can also use the ProvDmApi to create PROV data model specific nodes and relations.
        prov_dm_graph = 'my PROV DM graph'
        namespace = 'http://example.com'
        prov_api.create_provenance_graph(prov_dm_graph)
        inputProvId = pennprov.QualifiedName(namespace, 'input1')
        inputEntity = pennprov.NodeModel(type='ENTITY', attributes=[pennprov.Attribute(
            name=pennprov.QualifiedName(namespace, 'stringAttr'), value='paramValue', type='STRING')])
        prov_dm_api.store_node(resource=prov_dm_graph,
                               token=inputProvId, body=inputEntity)

        outputProvId = pennprov.QualifiedName(namespace, 'output1')
        outputEntity = pennprov.NodeModel(type='ENTITY', attributes=[pennprov.Attribute(
            name=pennprov.QualifiedName(namespace, 'longAttr'), value=16, type='LONG')])
        prov_dm_api.store_node(resource=prov_dm_graph,
                               token=outputProvId, body=outputEntity)

        wasDerivedFrom = pennprov.RelationModel(
            type='DERIVATION', subject_id=outputProvId, object_id=inputProvId,
            attributes=[pennprov.Attribute(name=pennprov.QualifiedName(namespace, 'booleanAttr'), value=True, type='BOOLEAN'),
                        pennprov.Attribute(name=pennprov.QualifiedName(namespace, 'anotherStringAttr'), value='attrValue', type='STRING')])
        prov_dm_api.store_relation(resource=prov_dm_graph, body=wasDerivedFrom, label='wasDerivedFrom')

        # And stil use the base ProvenanceApi to retrieve information about the PROV DM graph
        edge = prov_api.get_edges_from(prov_dm_graph, outputProvId)
        pprint(edge)
    except ApiException as api_exception:
        print("Exception when calling server: %s\n" % api_exception)


if __name__ == '__main__':
    main()

```

## Getting Started - Docker

If you want to have a simple Docker container to test the above, do the following.

```bash
cd docker-container
docker-compose up
```

Then (after waiting some time!) open your Web browser to http://localhost:8088 and click on `Sign up`.  Create a new user called `YOUR_USERNAME` with password `YOUR_PASSWORD`.

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
*ProvDmApi* | [**store_node**](docs/ProvDmApi.md#store_node) | **PUT** /provdm/graphs/{resource}/nodes/{token} | Store a PROV DM node
*ProvDmApi* | [**store_relation**](docs/ProvDmApi.md#store_relation) | **POST** /provdm/graphs/{resource}/links/{label} | Store a relation between PROV DM tokens
*ProvenanceApi* | [**create_or_reset_provenance_graph**](docs/ProvenanceApi.md#create_or_reset_provenance_graph) | **PUT** /provenance/graphs/reset/{resource} | Create a provenance graph if it doesn&#39;t exist, or overwrite it if it does
*ProvenanceApi* | [**create_provenance_graph**](docs/ProvenanceApi.md#create_provenance_graph) | **PUT** /provenance/graphs/{resource} | Create a provenance graph
*ProvenanceApi* | [**get_connected_from**](docs/ProvenanceApi.md#get_connected_from) | **GET** /provenance/graphs/{resource}/nodes/{token}/neighbors/out | Get the outgoing neighbors of the given prov token
*ProvenanceApi* | [**get_connected_to**](docs/ProvenanceApi.md#get_connected_to) | **GET** /provenance/graphs/{resource}/nodes/{token}/neighbors/in | Get the incoming neighbors of the given prov token
*ProvenanceApi* | [**get_edges_from**](docs/ProvenanceApi.md#get_edges_from) | **GET** /provenance/graphs/{resource}/nodes/{token}/links/out | Get the outgoing edges of the given prov token
*ProvenanceApi* | [**get_edges_to**](docs/ProvenanceApi.md#get_edges_to) | **GET** /provenance/graphs/{resource}/nodes/{token}/links/in | Get the incoming edges of the given prov token
*ProvenanceApi* | [**get_provenance_data**](docs/ProvenanceApi.md#get_provenance_data) | **GET** /provenance/graphs/{resource}/nodes/{token} | Get the tuple associated with a provenance token
*ProvenanceApi* | [**get_provenance_location**](docs/ProvenanceApi.md#get_provenance_location) | **GET** /provenance/graphs/{resource}/nodes/{token}/location | Get the location of a provenance token
*ProvenanceApi* | [**get_provenance_nodes**](docs/ProvenanceApi.md#get_provenance_nodes) | **GET** /provenance/graphs/{resource}/nodes | Get the provenance graph&#39;s nodes
*ProvenanceApi* | [**get_subgraphs**](docs/ProvenanceApi.md#get_subgraphs) | **POST** /provenance/graphs/{resource}/subgraphs | Get a provenance graph as a sequence of subgraphs
*ProvenanceApi* | [**store_provenance_link**](docs/ProvenanceApi.md#store_provenance_link) | **POST** /provenance/graphs/{resource}/links | Store a provenance link between tokens
*ProvenanceApi* | [**store_provenance_node**](docs/ProvenanceApi.md#store_provenance_node) | **PUT** /provenance/graphs/{resource}/nodes/{token} | Store a provenance token with its location
*ProvenanceApi* | [**store_subgraph**](docs/ProvenanceApi.md#store_subgraph) | **POST** /provenance/graphs/{resource}/subgraphs/store | Store a subgraph to a provenance graph


## Documentation For Models

 - [Attribute](docs/Attribute.md)
 - [FieldModel](docs/FieldModel.md)
 - [GroupDetails](docs/GroupDetails.md)
 - [IDModel](docs/IDModel.md)
 - [LinkInfo](docs/LinkInfo.md)
 - [LinkInstance](docs/LinkInstance.md)
 - [NodeInfo](docs/NodeInfo.md)
 - [NodeInstance](docs/NodeInstance.md)
 - [NodeModel](docs/NodeModel.md)
 - [OrgDetails](docs/OrgDetails.md)
 - [ProvEdgeModel](docs/ProvEdgeModel.md)
 - [ProvEdgeSetModel](docs/ProvEdgeSetModel.md)
 - [ProvNodeMapModel](docs/ProvNodeMapModel.md)
 - [ProvSpecifierModel](docs/ProvSpecifierModel.md)
 - [ProvTokenSetModel](docs/ProvTokenSetModel.md)
 - [QualifiedName](docs/QualifiedName.md)
 - [RankInstance](docs/RankInstance.md)
 - [RelationModel](docs/RelationModel.md)
 - [ResponseError](docs/ResponseError.md)
 - [StoreLinkModel](docs/StoreLinkModel.md)
 - [StoreNodeModel](docs/StoreNodeModel.md)
 - [SubgraphInstance](docs/SubgraphInstance.md)
 - [SubgraphTemplate](docs/SubgraphTemplate.md)
 - [TupleWithSchemaModel](docs/TupleWithSchemaModel.md)
 - [UserCredentials](docs/UserCredentials.md)
 - [UserInfo](docs/UserInfo.md)
 - [WebToken](docs/WebToken.md)
 - [BooleanAttribute](docs/BooleanAttribute.md)
 - [BooleanFieldModel](docs/BooleanFieldModel.md)
 - [DoubleAttribute](docs/DoubleAttribute.md)
 - [DoubleFieldModel](docs/DoubleFieldModel.md)
 - [IntAttribute](docs/IntAttribute.md)
 - [IntegerFieldModel](docs/IntegerFieldModel.md)
 - [LongAttribute](docs/LongAttribute.md)
 - [LongFieldModel](docs/LongFieldModel.md)
 - [MultiFieldModel](docs/MultiFieldModel.md)
 - [ProvExpressionModel](docs/ProvExpressionModel.md)
 - [ProvLocationModel](docs/ProvLocationModel.md)
 - [ProvSpecifierFieldModel](docs/ProvSpecifierFieldModel.md)
 - [ProvTokenFieldModel](docs/ProvTokenFieldModel.md)
 - [ProvTokenModel](docs/ProvTokenModel.md)
 - [QualifiedNameAttribute](docs/QualifiedNameAttribute.md)
 - [QualifiedNameFieldModel](docs/QualifiedNameFieldModel.md)
 - [StringAttribute](docs/StringAttribute.md)
 - [StringFieldModel](docs/StringFieldModel.md)


## Documentation For Authorization


## jwt

- **Type**: API key
- **API key parameter name**: api_key
- **Location**: HTTP header

