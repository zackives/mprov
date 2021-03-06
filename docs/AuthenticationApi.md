# pennprov.AuthenticationApi

All URIs are relative to *http://localhost:8088*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_credential**](AuthenticationApi.md#add_credential) | **POST** /auth/services/{service}/user/{username} | Adds a service credential for the user
[**add_group**](AuthenticationApi.md#add_group) | **POST** /auth/organizations/{organization}/group/{group} | Adds a permissions group to an organization
[**add_organization**](AuthenticationApi.md#add_organization) | **POST** /auth/organizations/{orgname} | Adds an organization
[**add_subgroup_to_group**](AuthenticationApi.md#add_subgroup_to_group) | **POST** /auth/groups/{groupname}/group/{subgroup} | Adds a subgroup to a group
[**add_user_to_group**](AuthenticationApi.md#add_user_to_group) | **POST** /auth/groups/{groupname}/user/{username} | Adds a user to a group
[**add_user_to_organization**](AuthenticationApi.md#add_user_to_organization) | **POST** /auth/organizations/{orgId}/user/{username} | Adds a user to an organization
[**create_new_user**](AuthenticationApi.md#create_new_user) | **POST** /auth/credentials/{username} | Creates a new user
[**get_group_from_id**](AuthenticationApi.md#get_group_from_id) | **GET** /auth/groups/id/{groupId} | Gets a group name from its integer ID
[**get_group_id**](AuthenticationApi.md#get_group_id) | **GET** /auth/groups/name/{groupName} | Gets a group&#39;s ID from its name
[**get_group_ids_for_user**](AuthenticationApi.md#get_group_ids_for_user) | **GET** /auth/credentials/{username}/groups/id | Gets the IDs of groups in which a user is directly a member
[**get_groups_for_user**](AuthenticationApi.md#get_groups_for_user) | **GET** /auth/credentials/{username}/groups | Gets the groups in which a user is directly a member
[**get_organization_from_id**](AuthenticationApi.md#get_organization_from_id) | **GET** /auth/organizations/id/{orgId} | Gets an organization name from its integer ID
[**get_organization_id**](AuthenticationApi.md#get_organization_id) | **GET** /auth/organizations/name/{orgName} | Gets an organization ID from its name
[**get_parent_group_ids**](AuthenticationApi.md#get_parent_group_ids) | **GET** /auth/groups/id/{groupId}/parents/id | Gets the IDs of parent groups
[**get_parent_groups**](AuthenticationApi.md#get_parent_groups) | **GET** /auth/groups/name/{groupName}/parents/name | Gets the groups in which a user is directly a member
[**get_token_route**](AuthenticationApi.md#get_token_route) | **POST** /auth/tokens/{username} | Requests a new token
[**get_user_info**](AuthenticationApi.md#get_user_info) | **GET** /auth/credentials/{username}/info | Gets a user&#39;s info
[**is_registered**](AuthenticationApi.md#is_registered) | **GET** /auth/services/{service}/user/{username} | Returns whether a user credential is valid for a service
[**is_valid_credential**](AuthenticationApi.md#is_valid_credential) | **POST** /auth/services/local/user/{username}/credential | Returns whether a local user credential is valid
[**update_user**](AuthenticationApi.md#update_user) | **PUT** /auth/credentials/{username} | Updates user properties


# **add_credential**
> UserInfo add_credential(service, username, credentials)

Adds a service credential for the user

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
    # Adds a service credential for the user
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.add_credential(service, username, credentials)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->add_credential: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service** | **str**|  | 
 **username** | **str**|  | 
 **credentials** | [**UserCredentials**](UserCredentials.md)|  | 

### Return type

[**UserInfo**](UserInfo.md)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_group**
> int add_group(organization, group, details)

Adds a permissions group to an organization

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
    # Adds a permissions group to an organization
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.add_group(organization, group, details)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->add_group: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **organization** | **int**|  | 
 **group** | **str**|  | 
 **details** | [**GroupDetails**](GroupDetails.md)|  | 

### Return type

**int**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_organization**
> int add_organization(orgname, details)

Adds an organization

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
    # Adds an organization
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.add_organization(orgname, details)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->add_organization: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgname** | **str**|  | 
 **details** | [**OrgDetails**](OrgDetails.md)|  | 

### Return type

**int**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_subgroup_to_group**
> int add_subgroup_to_group(groupname, subgroup)

Adds a subgroup to a group

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
    # Adds a subgroup to a group
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.add_subgroup_to_group(groupname, subgroup)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->add_subgroup_to_group: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **groupname** | **str**|  | 
 **subgroup** | **str**|  | 

### Return type

**int**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_user_to_group**
> int add_user_to_group(groupname, username)

Adds a user to a group

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
    # Adds a user to a group
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.add_user_to_group(groupname, username)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->add_user_to_group: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **groupname** | **str**|  | 
 **username** | **str**|  | 

### Return type

**int**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_user_to_organization**
> int add_user_to_organization(org_id, username)

Adds a user to an organization

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
    # Adds a user to an organization
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.add_user_to_organization(org_id, username)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->add_user_to_organization: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **int**|  | 
 **username** | **str**|  | 

### Return type

**int**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_new_user**
> UserInfo create_new_user(username, userfields)

Creates a new user

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
    # Creates a new user
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.create_new_user(username, userfields)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->create_new_user: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **str**|  | 
 **userfields** | [**UserInfo**](UserInfo.md)|  | 

### Return type

[**UserInfo**](UserInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_group_from_id**
> str get_group_from_id(group_id)

Gets a group name from its integer ID

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
    # Gets a group name from its integer ID
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.get_group_from_id(group_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->get_group_from_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **int**|  | 

### Return type

**str**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_group_id**
> int get_group_id(group_name)

Gets a group's ID from its name

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
    # Gets a group's ID from its name
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.get_group_id(group_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->get_group_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_name** | **str**|  | 

### Return type

**int**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_group_ids_for_user**
> list[object] get_group_ids_for_user(username)

Gets the IDs of groups in which a user is directly a member

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
    # Gets the IDs of groups in which a user is directly a member
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.get_group_ids_for_user(username)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->get_group_ids_for_user: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **str**|  | 

### Return type

**list[object]**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_groups_for_user**
> list[object] get_groups_for_user(username)

Gets the groups in which a user is directly a member

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
    # Gets the groups in which a user is directly a member
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.get_groups_for_user(username)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->get_groups_for_user: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **str**|  | 

### Return type

**list[object]**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_organization_from_id**
> str get_organization_from_id(org_id)

Gets an organization name from its integer ID

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
    # Gets an organization name from its integer ID
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.get_organization_from_id(org_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->get_organization_from_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **int**|  | 

### Return type

**str**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_organization_id**
> int get_organization_id(org_name)

Gets an organization ID from its name

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
    # Gets an organization ID from its name
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.get_organization_id(org_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->get_organization_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_name** | **str**|  | 

### Return type

**int**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_parent_group_ids**
> list[object] get_parent_group_ids(group_id)

Gets the IDs of parent groups

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
    # Gets the IDs of parent groups
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.get_parent_group_ids(group_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->get_parent_group_ids: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **int**|  | 

### Return type

**list[object]**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_parent_groups**
> list[object] get_parent_groups(group_name)

Gets the groups in which a user is directly a member

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
    # Gets the groups in which a user is directly a member
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.get_parent_groups(group_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->get_parent_groups: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_name** | **str**|  | 

### Return type

**list[object]**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_token_route**
> WebToken get_token_route(username, credentials)

Requests a new token

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
    # Requests a new token
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.get_token_route(username, credentials)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->get_token_route: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **str**|  | 
 **credentials** | [**UserCredentials**](UserCredentials.md)|  | 

### Return type

[**WebToken**](WebToken.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_user_info**
> UserInfo get_user_info(username)

Gets a user's info

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
    # Gets a user's info
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.get_user_info(username)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->get_user_info: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **str**|  | 

### Return type

[**UserInfo**](UserInfo.md)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **is_registered**
> bool is_registered(service, username)

Returns whether a user credential is valid for a service

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
    # Returns whether a user credential is valid for a service
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.is_registered(service, username)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->is_registered: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service** | **str**|  | 
 **username** | **str**|  | 

### Return type

**bool**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **is_valid_credential**
> bool is_valid_credential(username, credentials)

Returns whether a local user credential is valid

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
    # Returns whether a local user credential is valid
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.is_valid_credential(username, credentials)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->is_valid_credential: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **str**|  | 
 **credentials** | [**UserCredentials**](UserCredentials.md)|  | 

### Return type

**bool**

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_user**
> UserInfo update_user(username, userfields)

Updates user properties

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
    # Updates user properties
    # One-time initialization of client with a JWT token for
    # authentication.
    web_token = auth_api.get_token_route(username, credentials)
    token = web_token.token
    print("Setting token %s\n" % token)
    configuration.api_key["api_key"] = token
    api_response = api_instance.update_user(username, userfields)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AuthenticationApi->update_user: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **str**|  | 
 **userfields** | [**UserInfo**](UserInfo.md)|  | 

### Return type

[**UserInfo**](UserInfo.md)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

