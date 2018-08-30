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
api_instance = pennprov.ProvDmApi(pennprov.ApiClient(configuration))
resource = 'resource_example' # str | 
token = 'token_example' # str | 
body = pennprov.NodeModel() # NodeModel | 

try:
    # Store a PROV DM node
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
api_instance = pennprov.ProvDmApi(pennprov.ApiClient(configuration))
resource = 'resource_example' # str | 
body = pennprov.RelationModel() # RelationModel | 
label = 'label_example' # str | 

try:
    # Store a relation between PROV DM tokens
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

