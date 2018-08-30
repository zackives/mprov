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

from pennprov.models.tuple_with_schema_model import TupleWithSchemaModel  # noqa: F401,E501


class NodeInstance(object):
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
        'id': 'str',
        'tuple': 'TupleWithSchemaModel'
    }

    attribute_map = {
        'id': 'id',
        'tuple': 'tuple'
    }

    def __init__(self, id=None, tuple=None):  # noqa: E501
        """NodeInstance - a model defined in Swagger"""  # noqa: E501

        self._id = None
        self._tuple = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if tuple is not None:
            self.tuple = tuple

    @property
    def id(self):
        """Gets the id of this NodeInstance.  # noqa: E501


        :return: The id of this NodeInstance.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this NodeInstance.


        :param id: The id of this NodeInstance.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def tuple(self):
        """Gets the tuple of this NodeInstance.  # noqa: E501


        :return: The tuple of this NodeInstance.  # noqa: E501
        :rtype: TupleWithSchemaModel
        """
        return self._tuple

    @tuple.setter
    def tuple(self, tuple):
        """Sets the tuple of this NodeInstance.


        :param tuple: The tuple of this NodeInstance.  # noqa: E501
        :type: TupleWithSchemaModel
        """

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

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, NodeInstance):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
