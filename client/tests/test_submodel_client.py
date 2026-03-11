import json
import unittest
import logging
from unittest.mock import patch, Mock

from basyx.aas import model

from basyx_client.submodel import SubmodelClient
from basyx_client.utils import to_base64_urlencoded
from basyx.aas import adapter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)


class TestSubmodelClient(unittest.TestCase):
    """Tests for SubmodelClient that use mocking instead of a running BaSyx server."""
    TEST_IDS = {
        "test_id1": "test_id:9f3c2a8e-7b41-4d6f-a2c9-5e8b1f3d7a6c",
        "test_id2": "test_id:c7e4b2d9-3a6f-4f81-b5d2-8c1a9e7f4b63",
    }

    def setUp(self):
        self.base_url = "http://localhost:8081"
        self.client = SubmodelClient(self.base_url)
        self.default_submodel = self._create_submodel()

    def tearDown(self):
        pass  # No need to wipe repo with mocks

    def _create_submodel(self, submodel_id=None) -> model.Submodel:
        if submodel_id is None:
            submodel_id = self.TEST_IDS["test_id1"]

        return model.Submodel(
            id_=submodel_id,
            id_short="TEST_SUBMODEL"
        )

    @patch('basyx_client.submodel.requests.post')
    def test_create_submodel(self, mock_post):
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        # Test create_submodel
        result = self.client.create_submodel(submodel=self.default_submodel)

        # Expect successful result
        self.assertTrue(result)

    @patch('basyx_client.submodel.requests.post')
    def test_create_submodel_failure(self, mock_post):
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400  # Bad request
        mock_post.return_value = mock_response

        # Test create_submodel
        result = self.client.create_submodel(submodel=self.default_submodel)

        # Expect failure
        self.assertFalse(result)

    @patch('basyx_client.submodel.requests.get')
    def test_get_submodel(self, mock_get):
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        # Create a JSON representation of the submodel
        submodel_json = json.dumps(self.default_submodel, cls=adapter.json.AASToJsonEncoder)
        mock_response.text = submodel_json
        mock_get.return_value = mock_response

        # Test get_submodel
        remote_submodel = self.client.get_submodel(submodel_id=self.default_submodel.id)

        # Verify response
        self.assertEqual(self.default_submodel.id, remote_submodel.id)
        # Verify the request was called with correct arguments
        submodel_id_b64 = to_base64_urlencoded(self.default_submodel.id)
        mock_get.assert_called_once_with(f"{self.client.repo_url}/{submodel_id_b64}", timeout=30)

    @patch('basyx_client.submodel.requests.get')
    def test_get_submodel_failure(self, mock_get):
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 404  # Not found
        mock_get.return_value = mock_response

        # Test get_submodel
        remote_submodel = self.client.get_submodel(submodel_id=self.default_submodel.id)

        # Expect None for failure
        self.assertIsNone(remote_submodel)

    @patch('basyx_client.submodel.requests.put')
    def test_update_submodel(self, mock_put):
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_put.return_value = mock_response

        # Test update_submodel
        result = self.client.update_submodel(submodel=self.default_submodel)

        # Expect successful result
        self.assertTrue(result)

    @patch('basyx_client.submodel.requests.put')
    def test_update_submodel_failure(self, mock_put):
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400  # Bad request
        mock_put.return_value = mock_response

        # Test update_submodel
        result = self.client.update_submodel(submodel=self.default_submodel)

        # Expect failure
        self.assertFalse(result)

    @patch('basyx_client.submodel.requests.delete')
    def test_delete_submodel(self, mock_delete):
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        # Test delete_submodel
        result = self.client.delete_submodel(submodel_id=self.default_submodel.id)

        # Expect successful result
        self.assertTrue(result)

    @patch('basyx_client.submodel.requests.delete')
    def test_delete_submodel_failure(self, mock_delete):
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 404  # Not found
        mock_delete.return_value = mock_response

        # Test delete_submodel
        result = self.client.delete_submodel(submodel_id=self.default_submodel.id)

        # Expect failure
        self.assertFalse(result)

    @patch('basyx_client.submodel.requests.get')
    def test_get_submodels(self, mock_get):
        # Create test submodels
        test_submodels = [self._create_submodel(id_) for id_ in self.TEST_IDS.values()]

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        # Create a JSON representation of the submodels
        submodels_dict = {"result": test_submodels}
        submodels_json = json.dumps(submodels_dict, cls=adapter.json.AASToJsonEncoder)
        mock_response.text = submodels_json
        mock_get.return_value = mock_response

        # Test get_submodels
        page = self.client.get_submodels()

        # Verify response
        self.assertEqual(len(test_submodels), len(page.result))
        for i, submodel in enumerate(test_submodels):
            self.assertEqual(submodel.id, page.result[i].id)

    @patch('basyx_client.submodel.requests.get')
    def test_get_submodels_failure(self, mock_get):
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 500  # Server error
        mock_get.return_value = mock_response

        # Test get_submodels
        page = self.client.get_submodels()

        # Expect empty page for failure
        self.assertEqual(0, len(page.result))
        self.assertIsNone(page.cursor)


if __name__ == "__main__":
    unittest.main()
