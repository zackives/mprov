# pennprov.PermissionApi

All URIs are relative to *http://localhost:8088*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_permission**](PermissionApi.md#add_permission) | **POST** /perms/types/{permname} | Adds a new labeled permission type
[**get_group_permissions_on**](PermissionApi.md#get_group_permissions_on) | **GET** /perms/objects/{object}/group/{groupName} | Gets the group&#39;s permissions on an object
[**get_object_ids**](PermissionApi.md#get_object_ids) | **GET** /perms/name/{permname}/user/{username} | Gets the object ids for which the user has the given permission
[**get_permission_from_id**](PermissionApi.md#get_permission_from_id) | **GET** /perms/id/{id}/name | Gets a permission&#39;s name from its integer ID
[**get_permission_id**](PermissionApi.md#get_permission_id) | **GET** /perms/name/{name}/id | Gets a permission&#39;s ID from its name
[**get_user_permissions_on**](PermissionApi.md#get_user_permissions_on) | **GET** /perms/objects/{object}/user/{username} | Gets the user&#39;s permissions on an object
[**grant_group_permission_on**](PermissionApi.md#grant_group_permission_on) | **POST** /perms/objects/{object}/group/{groupName}/{permname} | Grants a group a permission on an object
[**grant_user_permission_on**](PermissionApi.md#grant_user_permission_on) | **POST** /perms/objects/{object}/user/{username}/{permname} | Grants a user a permission on an object
[**revoke_group_permission_on**](PermissionApi.md#revoke_group_permission_on) | **DELETE** /perms/objects/{object}/group/{groupName}/{permname} | Revokes a group a permission on an object
[**revoke_user_permission_on**](PermissionApi.md#revoke_user_permission_on) | **DELETE** /perms/objects/{object}/user/{username}/{permname} | Revokes a user a permission on an object


# **add_permission**
> int add_permission(permname)

Adds a new labeled permission type

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
    # Adds a new labeled permission type
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.add_permission(permname)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PermissionApi->add_permission: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **permname** | **str**|  | 

### Return type

**int**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_group_permissions_on**
> list[object] get_group_permissions_on(object, group_name)

Gets the group's permissions on an object

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
    # Gets the group's permissions on an object
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.get_group_permissions_on(object, group_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PermissionApi->get_group_permissions_on: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object** | **str**|  | 
 **group_name** | **str**|  | 

### Return type

**list[object]**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_object_ids**
> list[object] get_object_ids(permname, username)

Gets the object ids for which the user has the given permission

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
    # Gets the object ids for which the user has the given permission
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.get_object_ids(permname, username)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PermissionApi->get_object_ids: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **permname** | **str**|  | 
 **username** | **str**|  | 

### Return type

**list[object]**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_permission_from_id**
> str get_permission_from_id(id)

Gets a permission's name from its integer ID

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
    # Gets a permission's name from its integer ID
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.get_permission_from_id(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PermissionApi->get_permission_from_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

**str**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_permission_id**
> int get_permission_id(name)

Gets a permission's ID from its name

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
    # Gets a permission's ID from its name
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.get_permission_id(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PermissionApi->get_permission_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

**int**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_user_permissions_on**
> list[object] get_user_permissions_on(object, username)

Gets the user's permissions on an object

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
    # Gets the user's permissions on an object
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.get_user_permissions_on(object, username)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PermissionApi->get_user_permissions_on: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object** | **str**|  | 
 **username** | **str**|  | 

### Return type

**list[object]**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **grant_group_permission_on**
> bool grant_group_permission_on(object, group_name, permname)

Grants a group a permission on an object

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
    # Grants a group a permission on an object
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.grant_group_permission_on(object, group_name, permname)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PermissionApi->grant_group_permission_on: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object** | **str**|  | 
 **group_name** | **str**|  | 
 **permname** | **str**|  | 

### Return type

**bool**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **grant_user_permission_on**
> bool grant_user_permission_on(object, username, permname)

Grants a user a permission on an object

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
    # Grants a user a permission on an object
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.grant_user_permission_on(object, username, permname)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PermissionApi->grant_user_permission_on: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object** | **str**|  | 
 **username** | **str**|  | 
 **permname** | **str**|  | 

### Return type

**bool**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revoke_group_permission_on**
> bool revoke_group_permission_on(object, group_name, permname)

Revokes a group a permission on an object

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
    # Revokes a group a permission on an object
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.revoke_group_permission_on(object, group_name, permname)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PermissionApi->revoke_group_permission_on: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object** | **str**|  | 
 **group_name** | **str**|  | 
 **permname** | **str**|  | 

### Return type

**bool**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revoke_user_permission_on**
> bool revoke_user_permission_on(object, username, permname)

Revokes a user a permission on an object

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
    # Revokes a user a permission on an object
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.revoke_user_permission_on(object, username, permname)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PermissionApi->revoke_user_permission_on: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object** | **str**|  | 
 **username** | **str**|  | 
 **permname** | **str**|  | 

### Return type

**bool**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

