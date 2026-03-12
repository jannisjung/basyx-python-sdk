import json
import logging
import unittest
from unittest import SkipTest

import requests
from basyx.aas import adapter, model

from basyx_client.aas import AasClient
from basyx_client.submodel import SubmodelClient
from basyx_client.utils import to_base64_urlencoded

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

class TestAasClient(unittest.TestCase):
    """This test class assumes that there is a running BaSyx server at localhost:8081"""
    TEST_IDS = {
        "test_id1": "test_id:9f3c2a8e-7b41-4d6f-a2c9-5e8b1f3d7a6c",
        "test_id2": "test_id:c7e4b2d9-3a6f-4f81-b5d2-8c1a9e7f4b63",
    }
    def setUp(self):
        self.base_url = "http://localhost:8081"

        # Check if server is available
        try:
            response = requests.get(f"{self.base_url}/shells", timeout=5)
            if response.status_code != 200:
                raise SkipTest(f"BaSyx server not available at {self.base_url} (status: {response.status_code})")
        except requests.RequestException as e:
            raise SkipTest(f"BaSyx server not available at {self.base_url} (error: {e})") from e

        self.client = AasClient(self.base_url)
        self.default_shell = self._create_shell()

    def tearDown(self):
        try:
            self._wipe_repo()
        except Exception as e:
            logger.warning(f"Error during repo cleanup: {e}")

    def test_create_shell(self):
        try:
            created = self.client.create_shell(shell=self.default_shell)
            self.assertTrue(created)
        except requests.RequestException as e:
            self.skipTest(f"Network error during test: {e}")

    def test_create_and_get_shell(self):
        try:
            self.client.create_shell(shell=self.default_shell)

            remote_shell = self.client.get_shell(shell_id=self.default_shell.id)

            aas_id_b64 = to_base64_urlencoded(self.default_shell.id)
            aas_url = f"{self.client.repo_url}/{aas_id_b64}"
            certified_remote_shell = self._get_shell_manually(shell_endpoint=aas_url)

            self.assertEqual(certified_remote_shell.id, remote_shell.id)
        except requests.RequestException as e:
            self.skipTest(f"Network error during test: {e}")

    def test_get_shells(self):
        try:
            # Create test shells
            test_shells = [self._create_shell(id_) for id_ in self.TEST_IDS.values()]

            for shell in test_shells:
                self.client.create_shell(shell)

            # Get all shells
            result_page = self.client.get_shells()
            all_shells = result_page.result

            # Filter to only our test shells
            test_shell_ids = [shell.id for shell in test_shells]
            result_test_shells = [shell for shell in all_shells if shell.id in test_shell_ids]

            # Verify we got our test shells
            result_ids = [shell.id for shell in result_test_shells]
            self.assertEqual(len(result_test_shells), 2)
            for id_ in test_shell_ids:
                self.assertIn(id_, result_ids)
        except requests.RequestException as e:
            self.skipTest(f"Network error during test: {e}")


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

    def _get_shell_manually(self, shell_endpoint: str) -> model.AssetAdministrationShell:
        response = requests.get(shell_endpoint)
        shell_json = response.text
        return json.loads(shell_json, cls=adapter.json.AASFromJsonDecoder)

    def _wipe_repo(self):
        logger.info("Wiping Repo...")

        # Initialize submodel client for cleanup
        submodel_client = SubmodelClient(self.base_url)

        # First, get all submodels and delete test submodels
        try:
            submodels_response = requests.get(f"{self.base_url}/submodels")
            if submodels_response.status_code == 200:
                submodels_data = json.loads(submodels_response.text, cls=adapter.json.AASFromJsonDecoder)
                test_submodels = submodels_data.get("result", [])

                # Filter submodels that might be related to our tests
                submodel_endpoints = [
                    f"{self.base_url}/submodels/{to_base64_urlencoded(submodel.id)}"
                    for submodel in test_submodels
                    if "TEST" in (submodel.id_short or "").upper() or any(test_id in submodel.id for test_id in self.TEST_IDS.values())
                ]

                for endpoint in submodel_endpoints:
                    try:
                        response = requests.delete(endpoint, timeout=10)
                        if response.status_code == 204:
                            logger.info(f'Deleted submodel: "{endpoint}"')
                        else:
                            logger.debug(f"Submodel delete response code: {response.status_code} for {endpoint}")
                    except requests.RequestException as e:
                        logger.warning(f"Failed to delete submodel {endpoint}: {e}")
        except Exception as e:
            logger.warning(f"Error during submodel cleanup: {e}")

        # Then, get all shells and delete test shells
        try:
            response = requests.get(self.client.repo_url, timeout=10)
            if response.status_code == 200:
                json_shells = response.text
                deserialized_response = json.loads(json_shells, cls=adapter.json.AASFromJsonDecoder)
                basyx_shells = deserialized_response.get("result", [])

                shell_endpoints = [
                    f"{self.client.repo_url}/{to_base64_urlencoded(shell.id)}"
                    for shell in basyx_shells
                    if shell.id in self.TEST_IDS.values()
                ]

                for endpoint in shell_endpoints:
                    try:
                        response = requests.delete(endpoint, timeout=10)
                        if response.status_code == 204:
                            logger.info(f'Deleted shell: "{endpoint}"')
                        else:
                            logger.debug(f"Shell delete response code: {response.status_code} for {endpoint}")
                    except requests.RequestException as e:
                        logger.warning(f"Failed to delete shell {endpoint}: {e}")
        except Exception as e:
            logger.warning(f"Error during shell cleanup: {e}")


if __name__ == "__main__":
    unittest.main()