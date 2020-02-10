# coding: utf-8

"""
    Habitat repository and authorization API

    Habitat API  # noqa: E501

    OpenAPI spec version: V1.1.2
    Contact: zives@seas.upenn.edu
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from pennprov.models.prov_token_model import ProvTokenModel  # noqa: F401,E501
from pennprov.models.tuple_with_schema_model import TupleWithSchemaModel  # noqa: F401,E501


class StoreLinkModel(object):
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
        '_from': 'list[ProvTokenModel]',
        'to': 'ProvTokenModel',
        'label': 'str',
        'tuple_with_schema': 'TupleWithSchemaModel'
    }

    attribute_map = {
        '_from': 'from',
        'to': 'to',
        'label': 'label',
        'tuple_with_schema': 'tupleWithSchema'
    }

    def __init__(self, _from=None, to=None, label=None, tuple_with_schema=None):  # noqa: E501
        """StoreLinkModel - a model defined in Swagger"""  # noqa: E501

        self.__from = None
        self._to = None
        self._label = None
        self._tuple_with_schema = None
        self.discriminator = None

        self._from = _from
        self.to = to
        if label is not None:
            self.label = label
        if tuple_with_schema is not None:
            self.tuple_with_schema = tuple_with_schema

    @property
    def _from(self):
        """Gets the _from of this StoreLinkModel.  # noqa: E501


        :return: The _from of this StoreLinkModel.  # noqa: E501
        :rtype: list[ProvTokenModel]
        """
        return self.__from

    @_from.setter
    def _from(self, _from):
        """Sets the _from of this StoreLinkModel.


        :param _from: The _from of this StoreLinkModel.  # noqa: E501
        :type: list[ProvTokenModel]
        """
        if _from is None:
            raise ValueError("Invalid value for `_from`, must not be `None`")  # noqa: E501

        self.__from = _from

    @property
    def to(self):
        """Gets the to of this StoreLinkModel.  # noqa: E501


        :return: The to of this StoreLinkModel.  # noqa: E501
        :rtype: ProvTokenModel
        """
        return self._to

    @to.setter
    def to(self, to):
        """Sets the to of this StoreLinkModel.


        :param to: The to of this StoreLinkModel.  # noqa: E501
        :type: ProvTokenModel
        """
        if to is None:
            raise ValueError("Invalid value for `to`, must not be `None`")  # noqa: E501

        self._to = to

    @property
    def label(self):
        """Gets the label of this StoreLinkModel.  # noqa: E501


        :return: The label of this StoreLinkModel.  # noqa: E501
        :rtype: str
        """
        return self._label

    @label.setter
    def label(self, label):
        """Sets the label of this StoreLinkModel.


        :param label: The label of this StoreLinkModel.  # noqa: E501
        :type: str
        """

        self._label = label

    @property
    def tuple_with_schema(self):
        """Gets the tuple_with_schema of this StoreLinkModel.  # noqa: E501


        :return: The tuple_with_schema of this StoreLinkModel.  # noqa: E501
        :rtype: TupleWithSchemaModel
        """
        return self._tuple_with_schema

    @tuple_with_schema.setter
    def tuple_with_schema(self, tuple_with_schema):
        """Sets the tuple_with_schema of this StoreLinkModel.


        :param tuple_with_schema: The tuple_with_schema of this StoreLinkModel.  # noqa: E501
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
        if issubclass(StoreLinkModel, dict):
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
        if not isinstance(other, StoreLinkModel):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
