# pennprov.ProvDmApi

All URIs are relative to *http://localhost:8088*

Method | HTTP request | Description
------------- | ------------- | -------------
[**store_node**](ProvDmApi.md#store_node) | **PUT** /provdm/graphs/{resource}/nodes/{token} | Store a PROV DM node
[**store_relation**](ProvDmApi.md#store_relation) | **POST** /provdm/graphs/{resource}/links/{label} | Store a relation between PROV DM tokens


# **store_node**
> store_node(resource, token, body)

Store a PROV DM node

### Example
```python
from __future__ import print_function
import argparse
import getpass
import time
import pennprov
from pennprov.rest import ApiException
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', required=True, help='username')
parser.add_argument('-p', '--password',
                    help='password (will be prompted if omitted)')

args = parser.parse_args()
username = args.user
password = args.password if args.password else getpass.getpass()

"""Get a token and store a node"""
# create instances of the API classes
configuration = pennprov.configuration.Configuration()
configuration.host = "http://localhost:8088"
api_client = pennprov.ApiClient(configuration)    
auth_api = pennprov.AuthenticationApi(api_client)
prov_api = pennprov.ProvenanceApi(api_client)
prov_dm_api = pennprov.ProvDmApi(api_client)
credentials = pennprov.UserCredentials(password)
graph_name = "my_graph"

try:
    # Store a PROV DM node
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_instance.store_node(resource, token, body)
except ApiException as e:
    print("Exception when calling ProvDmApi->store_node: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 
 **token** | **str**|  | 
 **body** | [**NodeModel**](NodeModel.md)|  | 

### Return type

void (empty response body)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **store_relation**
> store_relation(resource, body, label)

Store a relation between PROV DM tokens

### Example
```python
from __future__ import print_function
import argparse
import getpass
import time
import pennprov
from pennprov.rest import ApiException
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', required=True, help='username')
parser.add_argument('-p', '--password',
                    help='password (will be prompted if omitted)')

args = parser.parse_args()
username = args.user
password = args.password if args.password else getpass.getpass()

"""Get a token and store a node"""
# create instances of the API classes
configuration = pennprov.configuration.Configuration()
configuration.host = "http://localhost:8088"
api_client = pennprov.ApiClient(configuration)    
auth_api = pennprov.AuthenticationApi(api_client)
prov_api = pennprov.ProvenanceApi(api_client)
prov_dm_api = pennprov.ProvDmApi(api_client)
credentials = pennprov.UserCredentials(password)
graph_name = "my_graph"

try:
    # Store a relation between PROV DM tokens
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_instance.store_relation(resource, body, label)
except ApiException as e:
    print("Exception when calling ProvDmApi->store_relation: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 
 **body** | [**RelationModel**](RelationModel.md)|  | 
 **label** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

