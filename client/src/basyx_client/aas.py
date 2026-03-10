import json
import logging

import requests
from basyx.aas import adapter, model

from basyx_client.pagination import Page
from basyx_client.utils import to_base64_urlencoded

logger = logging.getLogger(__name__)

class AasClient:
    def __init__(self, base_url: str, timeout:int=30):
        """
        Initialize the AAS Client

        :param base_url: The base URL of the AAS repository
        :param timeout: Request timeout in seconds (default: 30)
        """
        self.repo_url = base_url + "/shells"
        self.timeout = timeout
        self.default_headers = {'Content-Type': 'application/json'}

    def create_shell(self, shell: model.AssetAdministrationShell) -> bool:
        """
        Creates a new Asset Administration Shell

        :param shell: A basyx AssetAdministrationShell object
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            logger.debug(f"Uploading shell with ID: {shell.id}")

            # Convert basyx object to JSON
            json_shell = json.dumps(shell, cls=adapter.json.AASToJsonEncoder)

            # Call the API
            response = requests.post(
                url=self.repo_url,
                json=json.loads(json_shell),
                headers=self.default_headers,
                timeout=self.timeout
            )

            if response.status_code == 201:
                logger.debug(f"Successfully created shell with ID: {shell.id}")
                return True
            else:
                logger.warning(f"Failed to create shell: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.warning(f"Unexpected error when creating shell: {e}")
            return False

    def update_shell(self, shell: model.AssetAdministrationShell) -> bool:
        """
        Updates an existing Asset Administration Shell

        :param shell: A basyx AssetAdministrationShell object
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            logger.debug(f"Updating shell with ID: {shell.id}")

            # Convert basyx object to JSON
            json_shell = json.dumps(shell, cls=adapter.json.AASToJsonEncoder)

            # Encode the shell ID for the API
            encoded_id = to_base64_urlencoded(shell.id)
            shell_endpoint = f"{self.repo_url}/{encoded_id}"

            # Call the API
            response = requests.put(
                url=shell_endpoint,
                json=json.loads(json_shell),
                headers=self.default_headers,
                timeout=self.timeout
            )

            if response.status_code == 204:
                logger.debug(f"Successfully updated shell with ID: {shell.id}")
                return True
            else:
                logger.warning(f"Failed to update shell: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.warning(f"Unexpected error when updating shell: {e}")
            return False

    def get_shell(self, shell_id: str) -> model.AssetAdministrationShell | None:
        """
        Retrieves a specific Asset Administration Shell by ID

        :param shell_id: The ID of the shell to retrieve
        :return: The requested shell, or None if not found
        :rtype: model.AssetAdministrationShell | None
        """
        try:
            logger.debug(f"Retrieving shell with ID: {shell_id}")

            # Encode the shell ID for the API
            encoded_id = to_base64_urlencoded(shell_id)
            shell_endpoint = f"{self.repo_url}/{encoded_id}"

            # Call the API
            response = requests.get(shell_endpoint, timeout=self.timeout)

            if response.status_code == 200:
                shell_json = response.text
                result = json.loads(shell_json, cls=adapter.json.AASFromJsonDecoder)
                logger.debug(f"Successfully retrieved shell with ID: {shell_id}")
                return result
            else:
                logger.warning(f"Failed to get shell: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.warning(f"Unexpected error when retrieving shell: {e}")
            return None

    def get_shells(self, limit: int = 100) -> Page:
        """
        Retrieves all Asset Administration Shells

        :param limit: Maximum number of shells to retrieve
        :return: A page containing the list of shells
        :rtype: Page
        """
        try:
            logger.debug("Retrieving all shells")

            # Call the API
            response = requests.get(self.repo_url, params={'limit': limit}, timeout=self.timeout)

            if response.status_code == 200:
                json_shells = response.text
                deserialized_response = json.loads(json_shells, cls=adapter.json.AASFromJsonDecoder)
                shells = deserialized_response.get("result", [])
                cursor = deserialized_response.get("cursor")  # Extract cursor from response

                # Create a Page object with the results and cursor
                page = Page(result=shells, cursor=cursor)
                logger.debug(f"Successfully retrieved {len(shells)} shells")
                return page
            else:
                logger.warning(f"Failed to get shells: {response.status_code} - {response.text}")
                return Page(result=[], cursor=None)

        except Exception as e:
            logger.warning(f"Unexpected error when retrieving shells: {e}")
            return Page(result=[], cursor=None)

    def delete_shell(self, shell_id: str) -> bool:
        """
        Deletes an Asset Administration Shell

        :param shell_id: The ID of the shell to delete
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            logger.debug(f"Deleting shell with ID: {shell_id}")

            # Encode the shell ID for the API
            encoded_id = to_base64_urlencoded(shell_id)
            shell_endpoint = f"{self.repo_url}/{encoded_id}"

            # Call the API
            response = requests.delete(shell_endpoint, timeout=self.timeout)

            if response.status_code == 204:
                logger.debug(f"Successfully deleted shell with ID: {shell_id}")
                return True
            else:
                logger.warning(f"Failed to delete shell: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.warning(f"Unexpected error when deleting shell: {e}")
            return False
