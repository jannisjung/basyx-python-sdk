import json
import unittest
import logging

import requests
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
    """This test class assumes that there is a running BaSyx server at localhost:8081"""
    TEST_IDS = {
        "test_id1": "test_id:9f3c2a8e-7b41-4d6f-a2c9-5e8b1f3d7a6c",
        "test_id2": "test_id:c7e4b2d9-3a6f-4f81-b5d2-8c1a9e7f4b63",
    }
    def setUp(self):
        self.base_url = "http://localhost:8081"
        self.client = AasClient(self.base_url)
        self.default_shell = self._create_shell()

    def tearDown(self):
        self._wipe_repo()

    def test_create_shell(self):
        created = self.client.create_shell(shell=self.default_shell)
        self.assertTrue(created)

    def test_create_and_get_shell(self):
        self.client.create_shell(shell=self.default_shell)

        remote_shell = self.client.get_shell(shell_id=self.default_shell.id)
        
        aas_id_b64 = to_base64_urlencoded(self.default_shell.id)
        aas_url = f"{self.client.repo_url}/{aas_id_b64}"
        certified_remote_shell = self._get_shell_manually(shell_endpoint=aas_url)

        self.assertEqual(certified_remote_shell.id, remote_shell.id)

    def test_get_shells(self):
        result_shells = [self._create_shell(id_) for id_ in self.TEST_IDS.values()]

        for shell in result_shells:
            self.client.create_shell(shell)

        result_page = self.client.get_shells()
        result_shells = result_page.result

        certified_remote_shells = [self._get_shell_manually(
            shell_endpoint=f"{self.client.repo_url}/{to_base64_urlencoded(id_)}")
            for id_ in self.TEST_IDS.values()]

        result_ids = [shell.id for shell in result_shells]
        certified_remote_ids = [shell.id for shell in certified_remote_shells]

        self.assertGreaterEqual(len(result_shells), 2)
        for id_ in result_ids:
            self.assertIn(id_, certified_remote_ids)
        



    def _create_shell(self, shell_id=TEST_IDS["test_id1"]) -> model.AssetAdministrationShell:
        asset_information = model.AssetInformation(
                asset_kind=model.AssetKind.INSTANCE,
                global_asset_id="test_id")

        return  model.AssetAdministrationShell(
            id_=shell_id,
            id_short="TEST_AAS",
            asset_information=asset_information)
    
    def _get_shell_manually(self, shell_endpoint: str) -> model.AssetAdministrationShell:
        response = requests.get(shell_endpoint)
        shell_json = response.text
        return json.loads(shell_json, cls=adapter.json.AASFromJsonDecoder)
    
    def _wipe_repo(self):
        logger.info("Wiping Reo...")

        response = requests.get(self.client.repo_url)
        json_shells = response.text
        
        deserialized_response = json.loads(json_shells, cls=adapter.json.AASFromJsonDecoder)
        basyx_shells = deserialized_response.get("result")


        shell_endpoints = [
                f"{self.client.repo_url}/{to_base64_urlencoded(shell.id)}"
                for shell in basyx_shells
                if shell.id in self.TEST_IDS.values()]
        

        for endpoint in shell_endpoints:
            response = requests.delete(endpoint)
            if response.status_code != 204:
                logger.info(f"response code: {response.status_code}")

            logger.info(f'Deleted: "{endpoint}"')


if __name__ == "__main__":
    unittest.main()