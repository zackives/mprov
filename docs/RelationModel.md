# RelationModel

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attributes** | [**list[Attribute]**](Attribute.md) | It is an error to include attributes in a MEMEBERSHIP, ALTERNATE, or SPECIALIZATION relation | [optional] 
**type** | **str** |  | 
**subject_id** | [**QualifiedName**](QualifiedName.md) |  | 
**object_id** | [**QualifiedName**](QualifiedName.md) |  | 
**secondary_object_id** | [**QualifiedName**](QualifiedName.md) | It is an error to include a secondary object in a relation other than ASSOCIATION, DERIVATION, START, END, or DELEGATION | [optional] 
**relation_id** | [**QualifiedName**](QualifiedName.md) | It is an error to include attributes in a MEMEBERSHIP, ALTERNATE, or SPECIALIZATION relation | [optional] 
**time** | **datetime** | It is an error to include time in a relation other than GENERATION, USAGE, START, END, or INVALIDATION | [optional] 
**generation_id** | [**QualifiedName**](QualifiedName.md) | It is an error to include a generation id in a relation other than DERIVATION | [optional] 
**usage_id** | [**QualifiedName**](QualifiedName.md) | It is an error to include a usage id in a relation other than DERIVATION | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


