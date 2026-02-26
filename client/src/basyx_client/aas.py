import json
import logging
from typing import List
import requests

from basyx.aas import model
from basyx.aas import adapter

from pagination import Page
from basyx_client.utils import to_base64_urlencoded

logger = logging.getLogger(__name__)

class AasClient:
    def __init__(self, base_url):
        self.repo_url = base_url + "/shells"

    def create_shell(self, shell: model.AssetAdministrationShell) -> bool:
        logger.debug(f"Uploading shell with ID: {shell.id}")
        json_shell = json.dumps(shell, cls=adapter.json.AASToJsonEncoder)
        response = requests.post(
                url=self.repo_url,
                json=json.loads(json_shell) )

        if response.status_code != 201:
            logger.warning(f"Failed to upload shell: {response.text}")
            return False
        return True

    def update_shell(self, shell: model.AssetAdministrationShell) -> bool:
        pass

    def get_shell(self, shell_id: str) -> model.AssetAdministrationShell:
        shell_endpoint = f"{self.repo_url}/{to_base64_urlencoded(shell_id)}"
        response = requests.get(shell_endpoint)

        if response.status_code != 200:
            logger.warning(f'Failed to get shell with Id "{response.text}"')
            return None

        shell_json = response.text
        return json.loads(shell_json, cls=adapter.json.AASFromJsonDecoder)

    def get_shells(self, limit: int = 100) -> Page:
        # FIXME: set cursor and use limit!
        response = requests.get(self.repo_url)
        json_shells = response.text
        
        deserialized_response = json.loads(json_shells, cls=adapter.json.AASFromJsonDecoder)
        shells = deserialized_response.get("result")
        return Page(result=shells, cursor=None)

    def delete_shell(self, shell_id: str) -> bool:
        pass

"""
- AAS functions:
- `create_shell`
- `update_shell`
- `delete_shell`
- `add_submodel` – Creates the submodel in the submodel repository and references it to this shell
- `reference_submodel` – References an existing submodel
- `remove_submodel_reference`
- `get_submodel_references`
- `get_submodels`
- `delete_submodel` – Removes the reference from the shell and deletes the submodel from the submodel repository
"""