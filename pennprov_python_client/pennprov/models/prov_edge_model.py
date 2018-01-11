# coding: utf-8

"""
    Habitat repository and authorization API

    Habitat API  # noqa: E501

    OpenAPI spec version: V0.0.1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from pennprov.models.tuple_with_schema_model import TupleWithSchemaModel  # noqa: F401,E501


class ProvEdgeModel(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'endpoint_prov_token': 'str',
        'tuple_with_schema': 'TupleWithSchemaModel'
    }

    attribute_map = {
        'endpoint_prov_token': 'endpointProvToken',
        'tuple_with_schema': 'tupleWithSchema'
    }

    def __init__(self, endpoint_prov_token=None, tuple_with_schema=None):  # noqa: E501
        """ProvEdgeModel - a model defined in Swagger"""  # noqa: E501

        self._endpoint_prov_token = None
        self._tuple_with_schema = None
        self.discriminator = None

        self.endpoint_prov_token = endpoint_prov_token
        if tuple_with_schema is not None:
            self.tuple_with_schema = tuple_with_schema

    @property
    def endpoint_prov_token(self):
        """Gets the endpoint_prov_token of this ProvEdgeModel.  # noqa: E501


        :return: The endpoint_prov_token of this ProvEdgeModel.  # noqa: E501
        :rtype: str
        """
        return self._endpoint_prov_token

    @endpoint_prov_token.setter
    def endpoint_prov_token(self, endpoint_prov_token):
        """Sets the endpoint_prov_token of this ProvEdgeModel.


        :param endpoint_prov_token: The endpoint_prov_token of this ProvEdgeModel.  # noqa: E501
        :type: str
        """
        if endpoint_prov_token is None:
            raise ValueError("Invalid value for `endpoint_prov_token`, must not be `None`")  # noqa: E501

        self._endpoint_prov_token = endpoint_prov_token

    @property
    def tuple_with_schema(self):
        """Gets the tuple_with_schema of this ProvEdgeModel.  # noqa: E501


        :return: The tuple_with_schema of this ProvEdgeModel.  # noqa: E501
        :rtype: TupleWithSchemaModel
        """
        return self._tuple_with_schema

    @tuple_with_schema.setter
    def tuple_with_schema(self, tuple_with_schema):
        """Sets the tuple_with_schema of this ProvEdgeModel.


        :param tuple_with_schema: The tuple_with_schema of this ProvEdgeModel.  # noqa: E501
        :type: TupleWithSchemaModel
        """

        self._tuple_with_schema = tuple_with_schema

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, ProvEdgeModel):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
