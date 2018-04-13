# coding: utf-8

"""
    Habitat repository and authorization API

    Habitat API  # noqa: E501

    OpenAPI spec version: V1.0.0
    Contact: zives@seas.upenn.edu
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import unittest

import pennprov
from pennprov.api.authentication_api import AuthenticationApi  # noqa: E501
from pennprov.rest import ApiException


class TestAuthenticationApi(unittest.TestCase):
    """AuthenticationApi unit test stubs"""

    def setUp(self):
        self.api = pennprov.api.authentication_api.AuthenticationApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_add_credential(self):
        """Test case for add_credential

        Adds a service credential for the user  # noqa: E501
        """
        pass

    def test_add_group(self):
        """Test case for add_group

        Adds a permissions group to an organization  # noqa: E501
        """
        pass

    def test_add_organization(self):
        """Test case for add_organization

        Adds an organization  # noqa: E501
        """
        pass

    def test_add_subgroup_to_group(self):
        """Test case for add_subgroup_to_group

        Adds a subgroup to a group  # noqa: E501
        """
        pass

    def test_add_user_to_group(self):
        """Test case for add_user_to_group

        Adds a user to a group  # noqa: E501
        """
        pass

    def test_add_user_to_organization(self):
        """Test case for add_user_to_organization

        Adds a user to an organization  # noqa: E501
        """
        pass

    def test_create_new_user(self):
        """Test case for create_new_user

        Creates a new user  # noqa: E501
        """
        pass

    def test_get_group_from_id(self):
        """Test case for get_group_from_id

        Gets a group name from its integer ID  # noqa: E501
        """
        pass

    def test_get_group_id(self):
        """Test case for get_group_id

        Gets a group's ID from its name  # noqa: E501
        """
        pass

    def test_get_group_ids_for_user(self):
        """Test case for get_group_ids_for_user

        Gets the IDs of groups in which a user is directly a member  # noqa: E501
        """
        pass

    def test_get_groups_for_user(self):
        """Test case for get_groups_for_user

        Gets the groups in which a user is directly a member  # noqa: E501
        """
        pass

    def test_get_organization_from_id(self):
        """Test case for get_organization_from_id

        Gets an organization name from its integer ID  # noqa: E501
        """
        pass

    def test_get_organization_id(self):
        """Test case for get_organization_id

        Gets an organization ID from its name  # noqa: E501
        """
        pass

    def test_get_parent_group_ids(self):
        """Test case for get_parent_group_ids

        Gets the IDs of parent groups  # noqa: E501
        """
        pass

    def test_get_parent_groups(self):
        """Test case for get_parent_groups

        Gets the groups in which a user is directly a member  # noqa: E501
        """
        pass

    def test_get_token_route(self):
        """Test case for get_token_route

        Requests a new token  # noqa: E501
        """
        pass

    def test_get_user_info(self):
        """Test case for get_user_info

        Gets a user's info  # noqa: E501
        """
        pass

    def test_is_registered(self):
        """Test case for is_registered

        Returns whether a user credential is valid for a service  # noqa: E501
        """
        pass

    def test_is_valid_credential(self):
        """Test case for is_valid_credential

        Returns whether a local user credential is valid  # noqa: E501
        """
        pass

    def test_update_user(self):
        """Test case for update_user

        Updates user properties  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
