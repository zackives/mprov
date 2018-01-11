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


class UserInfo(object):
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
        'username': 'str',
        'email': 'str',
        'password': 'str',
        'firstname': 'str',
        'lastname': 'str',
        'street1': 'str',
        'street2': 'str',
        'city': 'str',
        'state': 'str',
        'zip': 'str',
        'country': 'str',
        'phone': 'str',
        'title': 'str',
        'organization': 'str'
    }

    attribute_map = {
        'username': 'username',
        'email': 'email',
        'password': 'password',
        'firstname': 'firstname',
        'lastname': 'lastname',
        'street1': 'street1',
        'street2': 'street2',
        'city': 'city',
        'state': 'state',
        'zip': 'zip',
        'country': 'country',
        'phone': 'phone',
        'title': 'title',
        'organization': 'organization'
    }

    def __init__(self, username=None, email=None, password=None, firstname=None, lastname=None, street1=None, street2=None, city=None, state=None, zip=None, country=None, phone=None, title=None, organization=None):
        """
        UserInfo - a model defined in Swagger
        """

        self._username = None
        self._email = None
        self._password = None
        self._firstname = None
        self._lastname = None
        self._street1 = None
        self._street2 = None
        self._city = None
        self._state = None
        self._zip = None
        self._country = None
        self._phone = None
        self._title = None
        self._organization = None

        if username is not None:
          self.username = username
        if email is not None:
          self.email = email
        if password is not None:
          self.password = password
        if firstname is not None:
          self.firstname = firstname
        if lastname is not None:
          self.lastname = lastname
        if street1 is not None:
          self.street1 = street1
        if street2 is not None:
          self.street2 = street2
        if city is not None:
          self.city = city
        if state is not None:
          self.state = state
        if zip is not None:
          self.zip = zip
        if country is not None:
          self.country = country
        if phone is not None:
          self.phone = phone
        if title is not None:
          self.title = title
        if organization is not None:
          self.organization = organization

    @property
    def username(self):
        """
        Gets the username of this UserInfo.

        :return: The username of this UserInfo.
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username):
        """
        Sets the username of this UserInfo.

        :param username: The username of this UserInfo.
        :type: str
        """

        self._username = username

    @property
    def email(self):
        """
        Gets the email of this UserInfo.

        :return: The email of this UserInfo.
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email):
        """
        Sets the email of this UserInfo.

        :param email: The email of this UserInfo.
        :type: str
        """

        self._email = email

    @property
    def password(self):
        """
        Gets the password of this UserInfo.

        :return: The password of this UserInfo.
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password):
        """
        Sets the password of this UserInfo.

        :param password: The password of this UserInfo.
        :type: str
        """

        self._password = password

    @property
    def firstname(self):
        """
        Gets the firstname of this UserInfo.

        :return: The firstname of this UserInfo.
        :rtype: str
        """
        return self._firstname

    @firstname.setter
    def firstname(self, firstname):
        """
        Sets the firstname of this UserInfo.

        :param firstname: The firstname of this UserInfo.
        :type: str
        """

        self._firstname = firstname

    @property
    def lastname(self):
        """
        Gets the lastname of this UserInfo.

        :return: The lastname of this UserInfo.
        :rtype: str
        """
        return self._lastname

    @lastname.setter
    def lastname(self, lastname):
        """
        Sets the lastname of this UserInfo.

        :param lastname: The lastname of this UserInfo.
        :type: str
        """

        self._lastname = lastname

    @property
    def street1(self):
        """
        Gets the street1 of this UserInfo.

        :return: The street1 of this UserInfo.
        :rtype: str
        """
        return self._street1

    @street1.setter
    def street1(self, street1):
        """
        Sets the street1 of this UserInfo.

        :param street1: The street1 of this UserInfo.
        :type: str
        """

        self._street1 = street1

    @property
    def street2(self):
        """
        Gets the street2 of this UserInfo.

        :return: The street2 of this UserInfo.
        :rtype: str
        """
        return self._street2

    @street2.setter
    def street2(self, street2):
        """
        Sets the street2 of this UserInfo.

        :param street2: The street2 of this UserInfo.
        :type: str
        """

        self._street2 = street2

    @property
    def city(self):
        """
        Gets the city of this UserInfo.

        :return: The city of this UserInfo.
        :rtype: str
        """
        return self._city

    @city.setter
    def city(self, city):
        """
        Sets the city of this UserInfo.

        :param city: The city of this UserInfo.
        :type: str
        """

        self._city = city

    @property
    def state(self):
        """
        Gets the state of this UserInfo.

        :return: The state of this UserInfo.
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """
        Sets the state of this UserInfo.

        :param state: The state of this UserInfo.
        :type: str
        """

        self._state = state

    @property
    def zip(self):
        """
        Gets the zip of this UserInfo.

        :return: The zip of this UserInfo.
        :rtype: str
        """
        return self._zip

    @zip.setter
    def zip(self, zip):
        """
        Sets the zip of this UserInfo.

        :param zip: The zip of this UserInfo.
        :type: str
        """

        self._zip = zip

    @property
    def country(self):
        """
        Gets the country of this UserInfo.

        :return: The country of this UserInfo.
        :rtype: str
        """
        return self._country

    @country.setter
    def country(self, country):
        """
        Sets the country of this UserInfo.

        :param country: The country of this UserInfo.
        :type: str
        """

        self._country = country

    @property
    def phone(self):
        """
        Gets the phone of this UserInfo.

        :return: The phone of this UserInfo.
        :rtype: str
        """
        return self._phone

    @phone.setter
    def phone(self, phone):
        """
        Sets the phone of this UserInfo.

        :param phone: The phone of this UserInfo.
        :type: str
        """

        self._phone = phone

    @property
    def title(self):
        """
        Gets the title of this UserInfo.

        :return: The title of this UserInfo.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """
        Sets the title of this UserInfo.

        :param title: The title of this UserInfo.
        :type: str
        """

        self._title = title

    @property
    def organization(self):
        """
        Gets the organization of this UserInfo.

        :return: The organization of this UserInfo.
        :rtype: str
        """
        return self._organization

    @organization.setter
    def organization(self, organization):
        """
        Sets the organization of this UserInfo.

        :param organization: The organization of this UserInfo.
        :type: str
        """

        self._organization = organization

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
        if not isinstance(other, UserInfo):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
