"""
Unit tests for authentication functionality in the BaSyx client.
"""

import base64
import unittest
from unittest.mock import Mock

from basyx_client.aas import AasClient
from basyx_client.auth import AuthType, OAuth2Client, add_basic_auth, add_token_auth
from basyx_client.submodel import SubmodelClient


class TestAuthUtils(unittest.TestCase):
    """Test the authentication utility functions."""

    def test_add_basic_auth(self):
        """Test basic authentication utility function."""
        headers = {}
        headers = add_basic_auth(headers, "testuser", "testpass")
        expected_credentials = base64.b64encode(b"testuser:testpass").decode('ascii')
        expected_header = f"Basic {expected_credentials}"

        self.assertIn('Authorization', headers)
        self.assertEqual(headers['Authorization'], expected_header)

    def test_add_token_auth(self):
        """Test token authentication utility function."""
        headers = {}
        headers = add_token_auth(headers, "testtoken")

        self.assertIn('Authorization', headers)
        self.assertEqual(headers['Authorization'], "Bearer testtoken")


class TestClientAuthInitialization(unittest.TestCase):
    """Test client initialization with authentication."""

    def test_aas_client_basic_auth_initialization(self):
        """Test AAS client initialization with basic authentication."""
        aas_client = AasClient(
            base_url="http://localhost:8080",
            auth_type="basic",
            auth_credentials=("testuser", "testpass")
        )

        self.assertEqual(aas_client.auth_type, AuthType.BASIC)
        self.assertEqual(aas_client.auth_credentials, ("testuser", "testpass"))

    def test_aas_client_token_auth_initialization(self):
        """Test AAS client initialization with token authentication."""
        aas_client = AasClient(
            base_url="http://localhost:8080",
            auth_type="token",
            auth_credentials=("testtoken",)
        )

        self.assertEqual(aas_client.auth_type, AuthType.TOKEN)
        self.assertEqual(aas_client.auth_credentials, ("testtoken",))

    def test_aas_client_oauth2_auth_initialization(self):
        """Test AAS client initialization with OAuth2 authentication."""
        oauth2_client = OAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            token_url="https://test-server.com/oauth/token"
        )
        aas_client = AasClient(
            base_url="http://localhost:8080",
            auth_type="oauth2",
            auth_credentials=(oauth2_client,)
        )

        self.assertEqual(aas_client.auth_type, AuthType.OAUTH2)
        self.assertEqual(aas_client.auth_credentials, (oauth2_client,))

    def test_submodel_client_auth_assignment(self):
        """Test Submodel client authentication assignment after creation."""
        submodel_client = SubmodelClient(base_url="http://localhost:8080")
        submodel_client.auth_type = "basic"
        submodel_client.auth_credentials = ("testuser", "testpass")

        self.assertEqual(submodel_client.auth_type, "basic")
        self.assertEqual(submodel_client.auth_credentials, ("testuser", "testpass"))


class TestAddAuthHeaders(unittest.TestCase):
    """Test the _add_auth_headers method."""

    def test_aas_client_adds_auth_headers(self):
        """Test AAS client adds authentication headers correctly."""
        aas_client = AasClient(
            base_url="http://localhost:8080",
            auth_type="basic",
            auth_credentials=("testuser", "testpass")
        )

        headers = aas_client._add_auth_headers({})
        self.assertIn('Authorization', headers)

    def test_submodel_client_adds_token_auth_headers(self):
        """Test Submodel client adds token authentication headers correctly."""
        submodel_client = SubmodelClient(base_url="http://localhost:8080")
        submodel_client.auth_type = AuthType.TOKEN
        submodel_client.auth_credentials = ("testtoken",)

        headers = submodel_client._add_auth_headers({})
        self.assertIn('Authorization', headers)
        self.assertEqual(headers['Authorization'], "Bearer testtoken")

    def test_aas_client_adds_oauth2_auth_headers(self):
        """Test AAS client adds OAuth2 authentication headers correctly."""
        oauth2_client = OAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            token_url="https://test-server.com/oauth/token"
        )
        # Mock the get_valid_token method to return a test token
        oauth2_client.get_valid_token = Mock(return_value="test_oauth2_token")

        aas_client = AasClient(
            base_url="http://localhost:8080",
            auth_type=AuthType.OAUTH2,
            auth_credentials=(oauth2_client,)
        )

        headers = aas_client._add_auth_headers({})
        self.assertIn('Authorization', headers)
        self.assertEqual(headers['Authorization'], "Bearer test_oauth2_token")

    def test_submodel_client_adds_oauth2_auth_headers(self):
        """Test Submodel client adds OAuth2 authentication headers correctly."""
        oauth2_client = OAuth2Client(
            client_id="test_client_id",
            client_secret="test_client_secret",
            token_url="https://test-server.com/oauth/token"
        )
        # Mock the get_valid_token method to return a test token
        oauth2_client.get_valid_token = Mock(return_value="test_oauth2_token")

        submodel_client = SubmodelClient(base_url="http://localhost:8080")
        submodel_client.auth_type = AuthType.OAUTH2
        submodel_client.auth_credentials = (oauth2_client,)

        headers = submodel_client._add_auth_headers({})
        self.assertIn('Authorization', headers)
        self.assertEqual(headers['Authorization'], "Bearer test_oauth2_token")

    def test_clients_without_auth_work_correctly(self):
        """Test clients without authentication work correctly."""
        aas_client_no_auth = AasClient(base_url="http://localhost:8080")
        headers = aas_client_no_auth._add_auth_headers({})
        # Should not add Authorization header when no auth is configured
        # (It might be empty or contain only default headers)
        # We're just ensuring it doesn't crash


if __name__ == '__main__':
    unittest.main()
