import json
import unittest
import logging
from unittest.mock import patch, Mock

from basyx.aas import model

from basyx_client.aas import AasClient
from basyx_client.utils import to_base64_urlencoded
from basyx.aas import adapter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)
class TestAasClient(unittest.TestCase):
    """Tests for AasClient that use mocking instead of a running BaSyx server."""
    TEST_IDS = {
        "test_id1": "test_id:9f3c2a8e-7b41-4d6f-a2c9-5e8b1f3d7a6c",
        "test_id2": "test_id:c7e4b2d9-3a6f-4f81-b5d2-8c1a9e7f4b63",
    }
    
    def setUp(self):
        self.base_url = "http://localhost:8081"
        self.client = AasClient(self.base_url)
        self.default_shell = self._create_shell()
    
    def tearDown(self):
        pass  # No need to wipe repo with mocks


    @patch('basyx_client.aas.requests.post')
    def test_create_shell(self, mock_post):
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        created = self.client.create_shell(shell=self.default_shell)
        self.assertTrue(created)
        # Verify the post request was called with correct arguments
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['url'], f"{self.base_url}/shells")
    
    @patch('basyx_client.aas.requests.post')
    def test_create_shell_failure(self, mock_post):
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400  # Bad request
        mock_post.return_value = mock_response
        
        created = self.client.create_shell(shell=self.default_shell)
        self.assertFalse(created)
    @patch('basyx_client.aas.requests.post')
    @patch('basyx_client.aas.requests.get')
    def test_create_and_get_shell(self, mock_get, mock_post):

        # Mock successful create response
        mock_post_response = Mock()
        mock_post_response.status_code = 201
        mock_post.return_value = mock_post_response
        
        # Mock successful get response
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        # Create a JSON representation of the shell
        shell_json = json.dumps(self.default_shell, cls=adapter.json.AASToJsonEncoder)
        mock_get_response.text = shell_json
        mock_get.return_value = mock_get_response
        
        # Test create
        self.client.create_shell(shell=self.default_shell)
        
        # Test get
        remote_shell = self.client.get_shell(shell_id=self.default_shell.id)
        
        # Verify responses
        self.assertEqual(self.default_shell.id, remote_shell.id)
        # Verify the requests were called with correct arguments
        aas_id_b64 = to_base64_urlencoded(self.default_shell.id)
        mock_get.assert_called_once_with(f"{self.client.repo_url}/{aas_id_b64}")
    @patch('basyx_client.aas.requests.get')
    def test_get_shell_failure(self, mock_get):

        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 404  # Not found
        mock_get.return_value = mock_response
        
        remote_shell = self.client.get_shell(shell_id=self.default_shell.id)
        self.assertIsNone(remote_shell)

    @patch('basyx_client.aas.requests.get')
    def test_get_shells(self, mock_get):

        # Create test shells
        test_shells = [self._create_shell(id_) for id_ in self.TEST_IDS.values()]
        
        # Mock successful get response
        mock_response = Mock()
        mock_response.status_code = 200
        # Create a JSON representation of the response
        response_data = {"result": test_shells}
        response_json = json.dumps(response_data, cls=adapter.json.AASToJsonEncoder)
        mock_response.text = response_json
        mock_get.return_value = mock_response
        
        result_page = self.client.get_shells()
        result_shells = result_page.result
        
        # Verify response
        self.assertEqual(len(result_shells), 2)
        result_ids = [shell.id for shell in result_shells]
        for id_ in self.TEST_IDS.values():
            self.assertIn(id_, result_ids)
        
        # Verify the request was called with correct arguments
        mock_get.assert_called_once_with(f"{self.base_url}/shells")

        


    def _create_shell(self, shell_id=None) -> model.AssetAdministrationShell:
        if shell_id is None:
            shell_id = self.TEST_IDS["test_id1"]

        asset_information = model.AssetInformation(
                asset_kind=model.AssetKind.INSTANCE,
                global_asset_id="test_id")

        return model.AssetAdministrationShell(
            id_=shell_id,
            id_short="TEST_AAS",
            asset_information=asset_information)


if __name__ == "__main__":
    unittest.main()
