# coding: utf-8

"""
    Habitat repository and authorization API

    Habitat API  # noqa: E501

    OpenAPI spec version: V1.1.0
    Contact: zives@seas.upenn.edu
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from pennprov.models.id_model import IDModel  # noqa: F401,E501
from pennprov.models.prov_specifier_model import ProvSpecifierModel  # noqa: F401,E501


class ProvLocationModel(object):
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
        'stream': 'IDModel',
        'field': 'str',
        'position': 'list[int]'
    }

    attribute_map = {
        'stream': 'stream',
        'field': 'field',
        'position': 'position'
    }

    def __init__(self, stream=None, field=None, position=None):  # noqa: E501
        """ProvLocationModel - a model defined in Swagger"""  # noqa: E501

        self._stream = None
        self._field = None
        self._position = None
        self.discriminator = None

        if stream is not None:
            self.stream = stream
        self.field = field
        self.position = position

    @property
    def stream(self):
        """Gets the stream of this ProvLocationModel.  # noqa: E501


        :return: The stream of this ProvLocationModel.  # noqa: E501
        :rtype: IDModel
        """
        return self._stream

    @stream.setter
    def stream(self, stream):
        """Sets the stream of this ProvLocationModel.


        :param stream: The stream of this ProvLocationModel.  # noqa: E501
        :type: IDModel
        """

        self._stream = stream

    @property
    def field(self):
        """Gets the field of this ProvLocationModel.  # noqa: E501


        :return: The field of this ProvLocationModel.  # noqa: E501
        :rtype: str
        """
        return self._field

    @field.setter
    def field(self, field):
        """Sets the field of this ProvLocationModel.


        :param field: The field of this ProvLocationModel.  # noqa: E501
        :type: str
        """
        if field is None:
            raise ValueError("Invalid value for `field`, must not be `None`")  # noqa: E501

        self._field = field

    @property
    def position(self):
        """Gets the position of this ProvLocationModel.  # noqa: E501


        :return: The position of this ProvLocationModel.  # noqa: E501
        :rtype: list[int]
        """
        return self._position

    @position.setter
    def position(self, position):
        """Sets the position of this ProvLocationModel.


        :param position: The position of this ProvLocationModel.  # noqa: E501
        :type: list[int]
        """
        if position is None:
            raise ValueError("Invalid value for `position`, must not be `None`")  # noqa: E501

        self._position = position

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
        if issubclass(ProvLocationModel, dict):
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
        if not isinstance(other, ProvLocationModel):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
