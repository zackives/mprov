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

from pennprov.models.prov_edge_model import ProvEdgeModel  # noqa: F401,E501


class ProvEdgeSetModel(object):
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
        'edges': 'list[ProvEdgeModel]'
    }

    attribute_map = {
        'edges': 'edges'
    }

    def __init__(self, edges=None):  # noqa: E501
        """ProvEdgeSetModel - a model defined in Swagger"""  # noqa: E501

        self._edges = None
        self.discriminator = None

        self.edges = edges

    @property
    def edges(self):
        """Gets the edges of this ProvEdgeSetModel.  # noqa: E501


        :return: The edges of this ProvEdgeSetModel.  # noqa: E501
        :rtype: list[ProvEdgeModel]
        """
        return self._edges

    @edges.setter
    def edges(self, edges):
        """Sets the edges of this ProvEdgeSetModel.


        :param edges: The edges of this ProvEdgeSetModel.  # noqa: E501
        :type: list[ProvEdgeModel]
        """
        if edges is None:
            raise ValueError("Invalid value for `edges`, must not be `None`")  # noqa: E501

        self._edges = edges

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
        if issubclass(ProvEdgeSetModel, dict):
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
        if not isinstance(other, ProvEdgeSetModel):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
