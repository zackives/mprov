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

from pennprov.models.prov_specifier_model import ProvSpecifierModel  # noqa: F401,E501


class ProvTokenModel(object):
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
        'token_value': 'str'
    }

    attribute_map = {
        'token_value': 'tokenValue'
    }

    def __init__(self, token_value=None):  # noqa: E501
        """ProvTokenModel - a model defined in Swagger"""  # noqa: E501

        self._token_value = None
        self.discriminator = None

        self.token_value = token_value

    @property
    def token_value(self):
        """Gets the token_value of this ProvTokenModel.  # noqa: E501


        :return: The token_value of this ProvTokenModel.  # noqa: E501
        :rtype: str
        """
        return self._token_value

    @token_value.setter
    def token_value(self, token_value):
        """Sets the token_value of this ProvTokenModel.


        :param token_value: The token_value of this ProvTokenModel.  # noqa: E501
        :type: str
        """
        if token_value is None:
            raise ValueError("Invalid value for `token_value`, must not be `None`")  # noqa: E501

        self._token_value = token_value

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
        if issubclass(ProvTokenModel, dict):
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
        if not isinstance(other, ProvTokenModel):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
