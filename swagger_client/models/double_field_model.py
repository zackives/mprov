# coding: utf-8

"""
    Habitat repository and authorization API

    Habitat API

    OpenAPI spec version: V0.0.1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class DoubleFieldModel(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
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
        'name': 'str',
        'value': 'float',
        'type': 'str'
    }

    attribute_map = {
        'name': 'name',
        'value': 'value',
        'type': 'type'
    }

    def __init__(self, name=None, value=None, type=None):
        """
        DoubleFieldModel - a model defined in Swagger
        """

        self._name = None
        self._value = None
        self._type = None

        self.name = name
        self.value = value
        self.type = type

    @property
    def name(self):
        """
        Gets the name of this DoubleFieldModel.

        :return: The name of this DoubleFieldModel.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this DoubleFieldModel.

        :param name: The name of this DoubleFieldModel.
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")

        self._name = name

    @property
    def value(self):
        """
        Gets the value of this DoubleFieldModel.

        :return: The value of this DoubleFieldModel.
        :rtype: float
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Sets the value of this DoubleFieldModel.

        :param value: The value of this DoubleFieldModel.
        :type: float
        """
        if value is None:
            raise ValueError("Invalid value for `value`, must not be `None`")

        self._value = value

    @property
    def type(self):
        """
        Gets the type of this DoubleFieldModel.

        :return: The type of this DoubleFieldModel.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Sets the type of this DoubleFieldModel.

        :param type: The type of this DoubleFieldModel.
        :type: str
        """
        if type is None:
            raise ValueError("Invalid value for `type`, must not be `None`")
        allowed_values = ["DOUBLE"]
        if type not in allowed_values:
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"
                .format(type, allowed_values)
            )

        self._type = type

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
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
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, DoubleFieldModel):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
