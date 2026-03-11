import json
import logging

import requests
from basyx.aas import adapter, model

from basyx_client.pagination import Page
from basyx_client.utils import to_base64_urlencoded

from basyx_client.aas import AasClient

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
        self.shell_client = AasClient(base_url, timeout)


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

    def get_submodels(self, limit: int = 100, cursor: str | None = None) -> Page:
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


    def add_submodel_element(self, submodel: model.Submodel, submodel_element: model.SubmodelElement, id_short_path: str) -> bool:
        """
        Adds a new submodel element to the given submodel at the specified id_short_path.

        If no id_short_path is provided, the submodel_element is added at the root level of the submodel.
        The last element of id_short_path must be a SubmodelElementCollection or SubmodelElementList 
        in which the submodel element shall be added.

        :param submodel: The submodel to add the element to
        :param submodel_element: The submodel element to add
        :param id_short_path: The idShort path where the element should be added (optional)
        :return: True if successful, False otherwise
        :rtype: bool
        """
        submodel_id: str = submodel.id

        # Encode the submodel ID for the API
        encoded_id = to_base64_urlencoded(submodel_id)
        endpoint = f"{self.repo_url}/{encoded_id}/submodel-elements{'/' + id_short_path or ''}"

        try:
            logger.debug(f"Adding submodel element to submodel with ID: {submodel_id}")

            json_submodel_element: str = json.dumps(submodel_element, cls=adapter.json.AASToJsonEncoder)

            response = requests.post(
                url=endpoint,
                json=json.loads(json_submodel_element),
                headers=self.default_headers,
                timeout=self.timeout
            )

            if response.status_code == 201:
                logger.debug(f"Successfully added SubmodelElement '{submodel_element.id_short}' to submodel with ID: '{submodel_id}'")
                return True
            else:
                logger.warning(f"Failed to add SubmodelElement '{submodel_element.id_short}' to submodel with ID: '{submodel_id}': {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.warning(f"Unexpected error when adding SubmodelElement: {e}")
            return False

    def update_submodel_element(self, submodel: model.Submodel, update: model.SubmodelElement, id_short_path: str) -> bool:
        """
        Updates an existing submodel element within a submodel (PUT).

        :param submodel: The submodel containing the element to update
        :param update: The updated submodel element
        :param id_short_path: The idShort path to the element (optional)
        :return: True if successful, False otherwise
        :rtype: bool
        """
        submodel_id: str = submodel.id

        # Encode the submodel ID for the API
        encoded_id = to_base64_urlencoded(submodel_id)
        endpoint = f"{self.repo_url}/{encoded_id}/submodel-elements/{id_short_path}"

        try:
            logger.debug(f"Updating submodel element in submodel with ID: {submodel_id}")

            json_submodel_element: str = json.dumps(update, cls=adapter.json.AASToJsonEncoder)

            response = requests.put(
                url=endpoint,
                json=json.loads(json_submodel_element),
                headers=self.default_headers,
                timeout=self.timeout
            )

            if response.status_code == 204:
                logger.debug(f"Successfully updated SubmodelElement '{update.id_short}' in submodel with ID: '{submodel_id}'")
                return True
            else:
                logger.warning(f"Failed to update SubmodelElement '{update.id_short}' in submodel with ID: '{submodel_id}': {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.warning(f"Unexpected error when updating SubmodelElement: {e}")
            return False

    def update_submodel_element_value(self, submodel: model.Submodel, value: object, id_short_path: str) -> bool:
        """
        Updates the value of an existing submodel element (PATCH operation).

        :param submodel: The submodel containing the element to update
        :param value: The new value for the element
        :param id_short_path: The idShort path to the element (optional)
        :return: True if successful, False otherwise
        :rtype: bool
        """
        submodel_id: str = submodel.id

        # Encode the submodel ID for the API
        encoded_id = to_base64_urlencoded(submodel_id)
        endpoint = f"{self.repo_url}/{encoded_id}/submodel-elements/{id_short_path}/$value"

        try:
            logger.debug(f"Updating value of submodel element in submodel with ID: {submodel_id}")

            # For PATCH operations, we typically send the raw value
            response = requests.patch(
                url=endpoint,
                json=value,
                headers=self.default_headers,
                timeout=self.timeout
            )

            if response.status_code == 204:
                logger.debug(f"Successfully updated value of submodel element in submodel with ID: '{submodel_id}'")
                return True
            else:
                logger.warning(f"Failed to update value of submodel element in submodel with ID: '{submodel_id}': {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.warning(f"Unexpected error when updating submodel element value: {e}")
            return False

    def get_submodel_element(self, submodel, id_short_path: str) -> model.SubmodelElement | None:
        pass

    def get_submodel_elements(self, submodel, limit: int = 100, cursor: str | None = None) -> Page:
        pass

    def delete_submodel_element(self, submodel: model.Submodel, id_short_path: str) -> bool:
        """
        Deletes a submodel element from the given submodel.

        :param submodel: The submodel containing the element to delete
        :param id_short_path: The idShort path to the element to delete
        :return: True if successful, False otherwise (e.g., if element didn't exist)
        :rtype: bool
        """
        submodel_id: str = submodel.id

        # Encode the submodel ID for the API
        encoded_id = to_base64_urlencoded(submodel_id)
        endpoint = f"{self.repo_url}/{encoded_id}/submodel-elements/{id_short_path}"

        try:
            logger.debug(f"Deleting submodel element from submodel with ID: {submodel_id}")

            response = requests.delete(
                url=endpoint,
                headers=self.default_headers,
                timeout=self.timeout
            )

            if response.status_code == 204:
                logger.debug(f"Successfully deleted submodel element from submodel with ID: '{submodel_id}'")
                return True
            else:
                logger.warning(f"Failed to delete submodel element from submodel with ID: '{submodel_id}': {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.warning(f"Unexpected error when deleting submodel element: {e}")
            return False

    def get_parent_id(self, submodel: model.Submodel) -> str | list[str] | None:
        """
        Returns the ID or a list of IDs of the parent shell(s) if the submodel is referenced by one or more shells.

        :param submodel: The submodel to get parent ID(s) for
        :return: The parent shell ID, a list of parent shell IDs, or None if the submodel is not referenced in any shell or doesn't exist
        :rtype: str | list[str] | None
        """
        submodel_id: str = submodel.id

        # TODO: Refactor: shells = while (self.shell_client.get_shells().curosr): shells +=  self.shell_client.get_shells(cursor=cursor).result
        shells: list[model.AssetAdministrationShell] = self.shell_client.get_shells().result

        # TODO: refactor this more pythonic
        result: list[model.AssetAdministrationShell] = []
        for shell in shells:
            if any(reference.key.value == submodel.id for reference in shell.submodel): # ty complains, that shell (type object) has no attribute submodel.
                result.append(shell)

        if len(result) == 1:
            return result[0].id
        return [shell.id for shell in result]


    def get_parent(self, submodel: model.Submodel, submodel_element: model.SubmodelElement = None, **kwargs) -> model.AssetAdministrationShell | list[model.AssetAdministrationShell] | model.Submodel | model.SubmodelElementCollection | model.SubmodelElementList | None:
        """
        Returns the parent object of a submodel or submodel element.

        The submodel_id is either extracted from the given Submodel, or directly given under **kwargs as "submodel_id".

        If submodel_element is None:
            - Returns an AAS if "id_short_path" is not in kwargs and the reference to this submodel is only found in one shell
            - Returns a list of AAS if the id_short_path is None or empty and the reference to this submodel is found in more than one shell

        If "id_short_path" is in kwargs:
            - Returns this submodel (with id submodel_id) if the id_short_path is not None or empty and the id_short_path depth is 1
            - Returns a SubmodelElementCollection if the id_short_path is not None and the id_short_path depth > 1 and the id_short_path doesn't end with f"[{numerical_value}]"
            - Returns a SubmodelElementList if the id_short_path is not None and the id_short_path depth > 1 and the id_short_path ends with f"[{numerical_value}]"

        If submodel_element is given or submodel_element_id_short is given in **kwargs but no "id_short_path" is given in **kwargs:
            - The provided submodel_element is checked for a assigned parent. If none parent is provided, the None is returned and a warning is loggedd
            - Else None is returned, and a warning is logged that either the submodel_element was not found, or there were multiple submodel elements found with the same id_short, so that no unambiguous parent could be determined

        Otherwise returns None.

        :param submodel: The submodel to get parent for (optional)
        :param submodel_element: The submodel element to get parent for (optional)
        :param kwargs: Additional keyword arguments including "submodel_id" and "id_short_path"
        :return: The parent object or None if not found
        :rtype: model.AssetAdministrationShell | list[model.AssetAdministrationShell] | model.Submodel | model.SubmodelElementCollection | model.SubmodelElementList | None
        """
        try:
            logger.debug("Retrieving parent object")

            # Extract parameters
            submodel_id = kwargs.get("submodel_id")
            id_short_path = kwargs.get("id_short_path")

            # If submodel is provided, use its ID
            if submodel is not None:
                submodel_id = submodel.id

            # If no submodel_id is available, return None
            if submodel_id is None:
                logger.warning("No submodel ID provided for parent retrieval")
                return None

            # Handle different cases based on the parameters
            if submodel_element is None:
                # Case 1: Get parent of submodel
                if id_short_path is None or id_short_path == "":
                    # Get parent AAS(es) of the submodel
                    parent_ids = self.get_parent_id(submodel)
                    if parent_ids is None:
                        return None
                    elif isinstance(parent_ids, str):
                        # Single parent - would need to fetch the actual AAS object
                        logger.debug(f"Single parent found for submodel {submodel_id}: {parent_ids}")
                        parent_id = parent_ids
                        return self.shell_client.get_shell(parent_id)
                    else:
                        # Multiple parents - would need to fetch the actual AAS objects
                        logger.debug(f"Multiple parents found for submodel {submodel_id}: {parent_ids}")
                        return [self.shell_client.get_shell(parent_id) for parent_id in parent_ids]
                elif id_short_path:
                    if not submodel:
                        submodel = self.get_submodel(submodel_id) if submodel_id else None
                    if not submodel:
                        return None
                    # Get parent within submodel based on id_short_path
                    path_parts = id_short_path.split('.')
                    if len(path_parts) == 1:
                        # Depth 1 - return the submodel itself
                        return submodel
                    else:
                        # Depth > 1 - would need to parse the path and find the parent element
                        logger.debug(f"Getting parent within submodel for path: {id_short_path}")
                        if path_parts[-1].endswith("[<numeric value>]"): # TODO:correct regex for "[<numeric value>]"
                            path_parts[-1] = path_parts[-1].split('[')[0] # TODO: de-magicify this: intended behavior "something[28374]" -> "something"
                        else:
                            path_parts.pop()
                        parent_id_short_path = path_parts.join('.')
                        return self.get_submodel_element(submodel, parent_id_short_path)

            elif submodel_element and not id_short_path:
                if not submodel_element.parent:
                    return None
                    logger.warning("Error when retrieving parent: Could not find parent of submodelElement")
                return submodel_element.parent

        except Exception as e:
            logger.warning(f"Unexpected error when retrieving parent: {e}")
            return None
