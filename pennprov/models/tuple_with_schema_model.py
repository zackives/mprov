# coding: utf-8

"""
    Habitat repository and authorization API

    Habitat API  # noqa: E501

    OpenAPI spec version: V1.1.1
    Contact: zives@seas.upenn.edu
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from pennprov.models.field_model import FieldModel  # noqa: F401,E501


class TupleWithSchemaModel(object):
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
        'schema_name': 'str',
        'lookup_keys': 'list[str]',
        'tuple': 'list[FieldModel]'
    }

    attribute_map = {
        'schema_name': 'schemaName',
        'lookup_keys': 'lookupKeys',
        'tuple': 'tuple'
    }

    def __init__(self, schema_name=None, lookup_keys=None, tuple=None):  # noqa: E501
        """TupleWithSchemaModel - a model defined in Swagger"""  # noqa: E501

        self._schema_name = None
        self._lookup_keys = None
        self._tuple = None
        self.discriminator = None

        self.schema_name = schema_name
        self.lookup_keys = lookup_keys
        self.tuple = tuple

    @property
    def schema_name(self):
        """Gets the schema_name of this TupleWithSchemaModel.  # noqa: E501


        :return: The schema_name of this TupleWithSchemaModel.  # noqa: E501
        :rtype: str
        """
        return self._schema_name

    @schema_name.setter
    def schema_name(self, schema_name):
        """Sets the schema_name of this TupleWithSchemaModel.


        :param schema_name: The schema_name of this TupleWithSchemaModel.  # noqa: E501
        :type: str
        """
        if schema_name is None:
            raise ValueError("Invalid value for `schema_name`, must not be `None`")  # noqa: E501

        self._schema_name = schema_name

    @property
    def lookup_keys(self):
        """Gets the lookup_keys of this TupleWithSchemaModel.  # noqa: E501


        :return: The lookup_keys of this TupleWithSchemaModel.  # noqa: E501
        :rtype: list[str]
        """
        return self._lookup_keys

    @lookup_keys.setter
    def lookup_keys(self, lookup_keys):
        """Sets the lookup_keys of this TupleWithSchemaModel.


        :param lookup_keys: The lookup_keys of this TupleWithSchemaModel.  # noqa: E501
        :type: list[str]
        """
        if lookup_keys is None:
            raise ValueError("Invalid value for `lookup_keys`, must not be `None`")  # noqa: E501

        self._lookup_keys = lookup_keys

    @property
    def tuple(self):
        """Gets the tuple of this TupleWithSchemaModel.  # noqa: E501


        :return: The tuple of this TupleWithSchemaModel.  # noqa: E501
        :rtype: list[FieldModel]
        """
        return self._tuple

    @tuple.setter
    def tuple(self, tuple):
        """Sets the tuple of this TupleWithSchemaModel.


        :param tuple: The tuple of this TupleWithSchemaModel.  # noqa: E501
        :type: list[FieldModel]
        """
        if tuple is None:
            raise ValueError("Invalid value for `tuple`, must not be `None`")  # noqa: E501

        self._tuple = tuple

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
        if issubclass(TupleWithSchemaModel, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, TupleWithSchemaModel):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
