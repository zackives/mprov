# swagger_client.ProvenanceApi

All URIs are relative to *http://localhost:8088*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_connected_from**](ProvenanceApi.md#get_connected_from) | **GET** /provenance/nodes/{token}/neighbors/out | Get the outgoing neighbors of the given prov token
[**get_connected_to**](ProvenanceApi.md#get_connected_to) | **GET** /provenance/nodes/{token}/neighbors/in | Get the incoming neighbors of the given prov token
[**get_edges_from**](ProvenanceApi.md#get_edges_from) | **GET** /provenance/nodes/{token}/links/out | Get the outgoing edges of the given prov token
[**get_edges_to**](ProvenanceApi.md#get_edges_to) | **GET** /provenance/nodes/{token}/links/in | Get the incoming edges of the given prov token
[**get_provenance_data**](ProvenanceApi.md#get_provenance_data) | **GET** /provenance/nodes/{token} | Get the tuple associated with a provenance token
[**get_provenance_location**](ProvenanceApi.md#get_provenance_location) | **GET** /provenance/nodes/{token}/location | Get the location of a provenance token
[**get_provenance_nodes**](ProvenanceApi.md#get_provenance_nodes) | **GET** /provenance/nodes | Get the provenance graph&#39;s nodes
[**store_provenance_link**](ProvenanceApi.md#store_provenance_link) | **POST** /provenance/links | Store a provenance link between tokens
[**store_provenance_node**](ProvenanceApi.md#store_provenance_node) | **PUT** /provenance/nodes/{token} | Store a provenance token with its location


# **get_connected_from**
> ProvTokenSetModel get_connected_from(token, label=label)

Get the outgoing neighbors of the given prov token

### Example 
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
swagger_client.configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# swagger_client.configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.ProvenanceApi()
token = 'token_example' # str | 
label = 'label_example' # str |  (optional)

try: 
    # Get the outgoing neighbors of the given prov token
    api_response = api_instance.get_connected_from(token, label=label)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProvenanceApi->get_connected_from: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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
> ProvTokenSetModel get_connected_to(token, label=label)

Get the incoming neighbors of the given prov token

### Example 
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
swagger_client.configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# swagger_client.configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.ProvenanceApi()
token = 'token_example' # str | 
label = 'label_example' # str |  (optional)

try: 
    # Get the incoming neighbors of the given prov token
    api_response = api_instance.get_connected_to(token, label=label)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProvenanceApi->get_connected_to: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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
> ProvEdgeSetModel get_edges_from(token, resource=resource)

Get the outgoing edges of the given prov token

### Example 
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
swagger_client.configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# swagger_client.configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.ProvenanceApi()
token = 'token_example' # str | 
resource = 'resource_example' # str |  (optional)

try: 
    # Get the outgoing edges of the given prov token
    api_response = api_instance.get_edges_from(token, resource=resource)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProvenanceApi->get_edges_from: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**|  | 
 **resource** | **str**|  | [optional] 

### Return type

[**ProvEdgeSetModel**](ProvEdgeSetModel.md)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_edges_to**
> ProvEdgeSetModel get_edges_to(token, resource=resource)

Get the incoming edges of the given prov token

### Example 
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
swagger_client.configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# swagger_client.configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.ProvenanceApi()
token = 'token_example' # str | 
resource = 'resource_example' # str |  (optional)

try: 
    # Get the incoming edges of the given prov token
    api_response = api_instance.get_edges_to(token, resource=resource)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProvenanceApi->get_edges_to: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**|  | 
 **resource** | **str**|  | [optional] 

### Return type

[**ProvEdgeSetModel**](ProvEdgeSetModel.md)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_provenance_data**
> TupleWithSchemaModel get_provenance_data(token)

Get the tuple associated with a provenance token

### Example 
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
swagger_client.configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# swagger_client.configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.ProvenanceApi()
token = 'token_example' # str | 

try: 
    # Get the tuple associated with a provenance token
    api_response = api_instance.get_provenance_data(token)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProvenanceApi->get_provenance_data: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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
> ProvSpecifierModel get_provenance_location(token)

Get the location of a provenance token

### Example 
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
swagger_client.configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# swagger_client.configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.ProvenanceApi()
token = 'token_example' # str | 

try: 
    # Get the location of a provenance token
    api_response = api_instance.get_provenance_location(token)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProvenanceApi->get_provenance_location: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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
> ProvNodeMapModel get_provenance_nodes(resource=resource)

Get the provenance graph's nodes

### Example 
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
swagger_client.configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# swagger_client.configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.ProvenanceApi()
resource = 'resource_example' # str |  (optional)

try: 
    # Get the provenance graph's nodes
    api_response = api_instance.get_provenance_nodes(resource=resource)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProvenanceApi->get_provenance_nodes: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | [optional] 

### Return type

[**ProvNodeMapModel**](ProvNodeMapModel.md)

### Authorization

[jwt](../README.md#jwt)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **store_provenance_link**
> store_provenance_link(body)

Store a provenance link between tokens

### Example 
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
swagger_client.configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# swagger_client.configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.ProvenanceApi()
body = swagger_client.StoreLinkModel() # StoreLinkModel | 

try: 
    # Store a provenance link between tokens
    api_instance.store_provenance_link(body)
except ApiException as e:
    print("Exception when calling ProvenanceApi->store_provenance_link: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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
> store_provenance_node(token, body)

Store a provenance token with its location

### Example 
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: jwt
swagger_client.configuration.api_key['api_key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# swagger_client.configuration.api_key_prefix['api_key'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.ProvenanceApi()
token = 'token_example' # str | 
body = swagger_client.StoreNodeModel() # StoreNodeModel | 

try: 
    # Store a provenance token with its location
    api_instance.store_provenance_node(token, body)
except ApiException as e:
    print("Exception when calling ProvenanceApi->store_provenance_node: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

