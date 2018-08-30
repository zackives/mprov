# pennprov.ProvenanceApi

All URIs are relative to *http://localhost:8088*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_provenance_graph**](ProvenanceApi.md#create_provenance_graph) | **PUT** /provenance/graphs/{resource} | Create a provenance graph
[**get_connected_from**](ProvenanceApi.md#get_connected_from) | **GET** /provenance/graphs/{resource}/nodes/{token}/neighbors/out | Get the outgoing neighbors of the given prov token
[**get_connected_to**](ProvenanceApi.md#get_connected_to) | **GET** /provenance/graphs/{resource}/nodes/{token}/neighbors/in | Get the incoming neighbors of the given prov token
[**get_edges_from**](ProvenanceApi.md#get_edges_from) | **GET** /provenance/graphs/{resource}/nodes/{token}/links/out | Get the outgoing edges of the given prov token
[**get_edges_to**](ProvenanceApi.md#get_edges_to) | **GET** /provenance/graphs/{resource}/nodes/{token}/links/in | Get the incoming edges of the given prov token
[**get_provenance_data**](ProvenanceApi.md#get_provenance_data) | **GET** /provenance/graphs/{resource}/nodes/{token} | Get the tuple associated with a provenance token
[**get_provenance_location**](ProvenanceApi.md#get_provenance_location) | **GET** /provenance/graphs/{resource}/nodes/{token}/location | Get the location of a provenance token
[**get_provenance_nodes**](ProvenanceApi.md#get_provenance_nodes) | **GET** /provenance/graphs/{resource}/nodes | Get the provenance graph&#39;s nodes
[**store_provenance_link**](ProvenanceApi.md#store_provenance_link) | **POST** /provenance/graphs/{resource}/links | Store a provenance link between tokens
[**store_provenance_node**](ProvenanceApi.md#store_provenance_node) | **PUT** /provenance/graphs/{resource}/nodes/{token} | Store a provenance token with its location


# **create_provenance_graph**
> create_provenance_graph(resource)

Create a provenance graph

### Example
```python
from __future__ import print_function
import time
import pennprov
from pennprov.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
configuration = pennprov.Configuration()
configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = pennprov.ProvenanceApi(pennprov.ApiClient(configuration))
resource = 'resource_example' # str | 

try:
    # Create a provenance graph
    api_instance.create_provenance_graph(resource)
except ApiException as e:
    print("Exception when calling ProvenanceApi->create_provenance_graph: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_connected_from**
> ProvTokenSetModel get_connected_from(resource, token, label=label)

Get the outgoing neighbors of the given prov token

### Example
```python
from __future__ import print_function
import time
import pennprov
from pennprov.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
configuration = pennprov.Configuration()
configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = pennprov.ProvenanceApi(pennprov.ApiClient(configuration))
resource = 'resource_example' # str | 
token = 'token_example' # str | 
label = 'label_example' # str |  (optional)

try:
    # Get the outgoing neighbors of the given prov token
    api_response = api_instance.get_connected_from(resource, token, label=label)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProvenanceApi->get_connected_from: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 
 **token** | **str**|  | 
 **label** | **str**|  | [optional] 

### Return type

[**ProvTokenSetModel**](ProvTokenSetModel.md)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_connected_to**
> ProvTokenSetModel get_connected_to(resource, token, label=label)

Get the incoming neighbors of the given prov token

### Example
```python
from __future__ import print_function
import time
import pennprov
from pennprov.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
configuration = pennprov.Configuration()
configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = pennprov.ProvenanceApi(pennprov.ApiClient(configuration))
resource = 'resource_example' # str | 
token = 'token_example' # str | 
label = 'label_example' # str |  (optional)

try:
    # Get the incoming neighbors of the given prov token
    api_response = api_instance.get_connected_to(resource, token, label=label)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProvenanceApi->get_connected_to: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 
 **token** | **str**|  | 
 **label** | **str**|  | [optional] 

### Return type

[**ProvTokenSetModel**](ProvTokenSetModel.md)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_edges_from**
> ProvEdgeSetModel get_edges_from(resource, token)

Get the outgoing edges of the given prov token

### Example
```python
from __future__ import print_function
import time
import pennprov
from pennprov.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
configuration = pennprov.Configuration()
configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = pennprov.ProvenanceApi(pennprov.ApiClient(configuration))
resource = 'resource_example' # str | 
token = 'token_example' # str | 

try:
    # Get the outgoing edges of the given prov token
    api_response = api_instance.get_edges_from(resource, token)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProvenanceApi->get_edges_from: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 
 **token** | **str**|  | 

### Return type

[**ProvEdgeSetModel**](ProvEdgeSetModel.md)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_edges_to**
> ProvEdgeSetModel get_edges_to(resource, token)

Get the incoming edges of the given prov token

### Example
```python
from __future__ import print_function
import time
import pennprov
from pennprov.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
configuration = pennprov.Configuration()
configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = pennprov.ProvenanceApi(pennprov.ApiClient(configuration))
resource = 'resource_example' # str | 
token = 'token_example' # str | 

try:
    # Get the incoming edges of the given prov token
    api_response = api_instance.get_edges_to(resource, token)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProvenanceApi->get_edges_to: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 
 **token** | **str**|  | 

### Return type

[**ProvEdgeSetModel**](ProvEdgeSetModel.md)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_provenance_data**
> TupleWithSchemaModel get_provenance_data(resource, token)

Get the tuple associated with a provenance token

### Example
```python
from __future__ import print_function
import time
import pennprov
from pennprov.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
configuration = pennprov.Configuration()
configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = pennprov.ProvenanceApi(pennprov.ApiClient(configuration))
resource = 'resource_example' # str | 
token = 'token_example' # str | 

try:
    # Get the tuple associated with a provenance token
    api_response = api_instance.get_provenance_data(resource, token)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProvenanceApi->get_provenance_data: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 
 **token** | **str**|  | 

### Return type

[**TupleWithSchemaModel**](TupleWithSchemaModel.md)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_provenance_location**
> ProvSpecifierModel get_provenance_location(resource, token)

Get the location of a provenance token

### Example
```python
from __future__ import print_function
import time
import pennprov
from pennprov.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
configuration = pennprov.Configuration()
configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = pennprov.ProvenanceApi(pennprov.ApiClient(configuration))
resource = 'resource_example' # str | 
token = 'token_example' # str | 

try:
    # Get the location of a provenance token
    api_response = api_instance.get_provenance_location(resource, token)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProvenanceApi->get_provenance_location: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 
 **token** | **str**|  | 

### Return type

[**ProvSpecifierModel**](ProvSpecifierModel.md)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_provenance_nodes**
> ProvNodeMapModel get_provenance_nodes(resource)

Get the provenance graph's nodes

### Example
```python
from __future__ import print_function
import time
import pennprov
from pennprov.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
configuration = pennprov.Configuration()
configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = pennprov.ProvenanceApi(pennprov.ApiClient(configuration))
resource = 'resource_example' # str | 

try:
    # Get the provenance graph's nodes
    api_response = api_instance.get_provenance_nodes(resource)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProvenanceApi->get_provenance_nodes: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 

### Return type

[**ProvNodeMapModel**](ProvNodeMapModel.md)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **store_provenance_link**
> store_provenance_link(resource, body)

Store a provenance link between tokens

### Example
```python
from __future__ import print_function
import time
import pennprov
from pennprov.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
configuration = pennprov.Configuration()
configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = pennprov.ProvenanceApi(pennprov.ApiClient(configuration))
resource = 'resource_example' # str | 
body = pennprov.StoreLinkModel() # StoreLinkModel | 

try:
    # Store a provenance link between tokens
    api_instance.store_provenance_link(resource, body)
except ApiException as e:
    print("Exception when calling ProvenanceApi->store_provenance_link: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 
 **body** | [**StoreLinkModel**](StoreLinkModel.md)|  | 

### Return type

void (empty response body)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **store_provenance_node**
> store_provenance_node(resource, token, body)

Store a provenance token with its location

### Example
```python
from __future__ import print_function
import time
import pennprov
from pennprov.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
configuration = pennprov.Configuration()
configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = pennprov.ProvenanceApi(pennprov.ApiClient(configuration))
resource = 'resource_example' # str | 
token = 'token_example' # str | 
body = pennprov.StoreNodeModel() # StoreNodeModel | 

try:
    # Store a provenance token with its location
    api_instance.store_provenance_node(resource, token, body)
except ApiException as e:
    print("Exception when calling ProvenanceApi->store_provenance_node: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 
 **token** | **str**|  | 
 **body** | [**StoreNodeModel**](StoreNodeModel.md)|  | 

### Return type

void (empty response body)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

