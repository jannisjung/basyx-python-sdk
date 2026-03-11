import json
import logging

import requests
from basyx.aas import adapter, model

from basyx_client.pagination import Page
from basyx_client.utils import to_base64_urlencoded

logger = logging.getLogger(__name__)


class SubmodelClient:
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize the Submodel Client

        :param base_url: The base URL of the AAS repository
        :param timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url
        self.repo_url = base_url + "/submodels"
        self.timeout = timeout
        self.default_headers = {'Content-Type': 'application/json'}

    def create_submodel(self, submodel: model.Submodel) -> bool:
        """
        Creates a new Submodel

        :param submodel: A basyx Submodel object
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            logger.debug(f"Creating submodel with ID: {submodel.id}")

            # Convert basyx object to JSON
            json_submodel = json.dumps(submodel, cls=adapter.json.AASToJsonEncoder)

            # Call the API
            response = requests.post(
                url=self.repo_url,
                json=json.loads(json_submodel),
                headers=self.default_headers,
                timeout=self.timeout
            )

            if response.status_code == 201:
                logger.debug(f"Successfully created submodel with ID: {submodel.id}")
                return True
            else:
                logger.warning(f"Failed to create submodel: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.warning(f"Unexpected error when creating submodel: {e}")
            return False

    def get_submodel(self, submodel_id: str) -> model.Submodel | None:
        """
        Retrieves a specific Submodel by ID

        :param submodel_id: The ID of the submodel to retrieve
        :return: The requested submodel, or None if not found
        :rtype: model.Submodel | None
        """
        try:
            logger.debug(f"Retrieving submodel with ID: {submodel_id}")

            # Encode the submodel ID for the API
            encoded_id = to_base64_urlencoded(submodel_id)
            submodel_endpoint = f"{self.repo_url}/{encoded_id}"

            # Call the API
            response = requests.get(submodel_endpoint, timeout=self.timeout)

            if response.status_code == 200:
                submodel_json = response.text
                result = json.loads(submodel_json, cls=adapter.json.AASFromJsonDecoder)
                logger.debug(f"Successfully retrieved submodel with ID: {submodel_id}")
                return result
            else:
                logger.warning(f"Failed to get submodel: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.warning(f"Unexpected error when retrieving submodel: {e}")
            return None

    def update_submodel(self, submodel: model.Submodel) -> bool:
        """
        Updates an existing Submodel

        :param submodel: A basyx Submodel object
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            logger.debug(f"Updating submodel with ID: {submodel.id}")

            # Convert basyx object to JSON
            json_submodel = json.dumps(submodel, cls=adapter.json.AASToJsonEncoder)

            # Encode the submodel ID for the API
            encoded_id = to_base64_urlencoded(submodel.id)
            submodel_endpoint = f"{self.repo_url}/{encoded_id}"

            # Call the API
            response = requests.put(
                url=submodel_endpoint,
                json=json.loads(json_submodel),
                headers=self.default_headers,
                timeout=self.timeout
            )

            if response.status_code == 204:
                logger.debug(f"Successfully updated submodel with ID: {submodel.id}")
                return True
            else:
                logger.warning(f"Failed to update submodel: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.warning(f"Unexpected error when updating submodel: {e}")
            return False

    def delete_submodel(self, submodel_id: str) -> bool:
        """
        Deletes a Submodel

        :param submodel_id: The ID of the submodel to delete
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            logger.debug(f"Deleting submodel with ID: {submodel_id}")

            # Encode the submodel ID for the API
            encoded_id = to_base64_urlencoded(submodel_id)
            submodel_endpoint = f"{self.repo_url}/{encoded_id}"

            # Call the API
            response = requests.delete(submodel_endpoint, timeout=self.timeout)

            if response.status_code == 204:
                logger.debug(f"Successfully deleted submodel with ID: {submodel_id}")
                return True
            else:
                logger.warning(f"Failed to delete submodel: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.warning(f"Unexpected error when deleting submodel: {e}")
            return False

    def get_submodels(self, limit: int = 100) -> Page:
        """
        Retrieves all Submodels

        :param limit: Maximum number of submodels to retrieve
        :return: A page containing the list of submodels
        :rtype: Page
        """
        try:
            logger.debug("Retrieving all submodels")

            # Call the API
            response = requests.get(self.repo_url, params={'limit': limit}, timeout=self.timeout)

            if response.status_code == 200:
                json_submodels = response.text
                deserialized_response = json.loads(json_submodels, cls=adapter.json.AASFromJsonDecoder)
                submodels = deserialized_response.get("result", [])
                cursor = deserialized_response.get("cursor")  # Extract cursor from response

                # Create a Page object with the results and cursor
                page = Page(result=submodels, cursor=cursor)
                logger.debug(f"Successfully retrieved {len(submodels)} submodels")
                return page
            else:
                logger.warning(f"Failed to get submodels: {response.status_code} - {response.text}")
                return Page(result=[], cursor=None)

        except Exception as e:
            logger.warning(f"Unexpected error when retrieving submodels: {e}")
            return Page(result=[], cursor=None)
