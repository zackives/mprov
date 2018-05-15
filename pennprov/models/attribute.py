# coding: utf-8

"""
    Habitat repository and authorization API

    Habitat API  # noqa: E501

    OpenAPI spec version: V1.0.1
    Contact: zives@seas.upenn.edu
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from pennprov.models.qualified_name import QualifiedName  # noqa: F401,E501


class Attribute(object):
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
        'name': 'QualifiedName',
        'value': 'object',
        'type': 'str'
    }

    attribute_map = {
        'name': 'name',
        'value': 'value',
        'type': 'type'
    }

    discriminator_value_class_map = {
        'BooleanAttribute': 'BooleanAttribute',
        'StringAttribute': 'StringAttribute',
        'LongAttribute': 'LongAttribute',
        'DoubleAttribute': 'DoubleAttribute',
        'QualifiedNameAttribute': 'QualifiedNameAttribute'
    }

    def __init__(self, name=None, value=None, type=None):  # noqa: E501
        """Attribute - a model defined in Swagger"""  # noqa: E501

        self._name = None
        self._value = None
        self._type = None
        self.discriminator = 'type'

        self.name = name
        self.value = value
        self.type = type

    @property
    def name(self):
        """Gets the name of this Attribute.  # noqa: E501


        :return: The name of this Attribute.  # noqa: E501
        :rtype: QualifiedName
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Attribute.


        :param name: The name of this Attribute.  # noqa: E501
        :type: QualifiedName
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def value(self):
        """Gets the value of this Attribute.  # noqa: E501


        :return: The value of this Attribute.  # noqa: E501
        :rtype: object
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this Attribute.


        :param value: The value of this Attribute.  # noqa: E501
        :type: object
        """
        if value is None:
            raise ValueError("Invalid value for `value`, must not be `None`")  # noqa: E501

        self._value = value

    @property
    def type(self):
        """Gets the type of this Attribute.  # noqa: E501


        :return: The type of this Attribute.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Attribute.


        :param type: The type of this Attribute.  # noqa: E501
        :type: str
        """
        if type is None:
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501
        allowed_values = ["BOOLEAN", "DOUBLE", "STRING", "LONG", "QUALIFIED_NAME"]  # noqa: E501
        if type not in allowed_values:
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"  # noqa: E501
                .format(type, allowed_values)
            )

        self._type = type

    def get_real_child_model(self, data):
        """Returns the real base class specified by the discriminator"""
        discriminator_value = data[self.discriminator].lower()
        return self.discriminator_value_class_map.get(discriminator_value)

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
        if not isinstance(other, Attribute):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
