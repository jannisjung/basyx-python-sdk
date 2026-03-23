import json
import logging

import requests
from basyx.aas import adapter, model

from basyx_client.auth import AuthType
from basyx_client.operation_handle import OperationHandle
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
        self.auth_type = None
        self.auth_credentials = None

    def _add_auth_headers(self, headers: dict | None = None) -> dict:
        """
        Add authentication headers to the request headers.

        :param headers: Original headers or None
        :return: Headers with authentication added, or empty dict if no auth needed
        """
        # If no auth configured, return original headers or empty dict
        if not self.auth_type or not self.auth_credentials:
            return headers if headers is not None else {}

        # Start with provided headers or empty dict
        auth_headers = headers.copy() if headers is not None else {}

        if self.auth_type == AuthType.BASIC:
            from basyx_client.auth import add_basic_auth
            username, password = self.auth_credentials
            auth_headers = add_basic_auth(auth_headers, username, password)
        elif self.auth_type == AuthType.TOKEN:
            from basyx_client.auth import add_token_auth
            token, = self.auth_credentials
            auth_headers = add_token_auth(auth_headers, token)
        elif self.auth_type == AuthType.OAUTH2:
            from basyx_client.auth import OAuth2Client, add_oauth2_auth
            oauth2_client: OAuth2Client = self.auth_credentials[0]
            auth_headers = add_oauth2_auth(auth_headers, oauth2_client)

        return auth_headers


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
            headers = self._add_auth_headers(self.default_headers)

            response = requests.post(
                url=self.repo_url,
                data=json_submodel,
                headers=headers,
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
            headers = self._add_auth_headers(self.default_headers)
            response = requests.get(submodel_endpoint, headers=headers, timeout=self.timeout)

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
            headers = self._add_auth_headers(self.default_headers)
            response = requests.put(
                url=submodel_endpoint,
                data=json_submodel,
                headers=headers,
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

            headers = self._add_auth_headers(self.default_headers)
            response = requests.delete(submodel_endpoint, headers=headers, timeout=self.timeout)

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
        :param cursor: Cursor for pagination
        :return: A page containing the list of submodels
        :rtype: Page
        """
        try:
            logger.debug("Retrieving all submodels")

            # Prepare query parameters
            params: dict[str, str | int] = {'limit': limit}
            if cursor:
                params['cursor'] = cursor

            # Call the API
            headers = self._add_auth_headers(self.default_headers)
            response = requests.get(self.repo_url, params=params, headers=headers, timeout=self.timeout)

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


    def add_submodel_element(self, submodel: model.Submodel, submodel_element: model.SubmodelElement, id_short_path: str = "") -> bool:
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

            headers = self._add_auth_headers(self.default_headers)
            response = requests.post(
                url=endpoint,
                data=json_submodel_element,
                headers=headers,
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

    def update_submodel_element(self, submodel: model.Submodel, update: model.SubmodelElement, id_short_path: str = "") -> bool:
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

            headers = self._add_auth_headers(self.default_headers)
            response = requests.put(
                url=endpoint,
                data=json_submodel_element,
                headers=headers,
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

    def update_submodel_element_value(self, submodel: model.Submodel, value: object, id_short_path: str = "") -> bool:
        """
        Updates the value of an existing submodel element (PATCH).

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
            if self.auth_type and self.auth_credentials:
                headers = self._add_auth_headers(self.default_headers)
                response = requests.patch(
                    url=endpoint,
                    json=value,
                    headers=headers,
                    timeout=self.timeout
                )
            else:
                response = requests.patch(
                    url=endpoint,
                    json=value,
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
        """
        Retrieves a specific submodel element by its idShort path.

        :param submodel: The submodel containing the element
        :param id_short_path: The idShort path to the element
        :return: The requested submodel element, or None if not found
        :rtype: model.SubmodelElement | None
        """
        submodel_id: str = submodel.id

        # Encode the submodel ID for the API
        encoded_id = to_base64_urlencoded(submodel_id)
        endpoint = f"{self.repo_url}/{encoded_id}/submodel-elements/{id_short_path}"

        try:
            logger.debug(f"Retrieving submodel element from submodel with ID: {submodel_id}")

            headers = self._add_auth_headers(self.default_headers)
            response = requests.get(
                url=endpoint,
                headers=headers,
                timeout=self.timeout
            )


            if response.status_code == 200:
                element_json = response.text
                result = json.loads(element_json, cls=adapter.json.AASFromJsonDecoder)
                logger.debug(f"Successfully retrieved submodel element from submodel with ID: '{submodel_id}'")
                return result
            else:
                logger.warning(f"Failed to get submodel element from submodel with ID: '{submodel_id}': {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.warning(f"Unexpected error when retrieving submodel element: {e}")
            return None

    def get_submodel_elements(self, submodel, limit: int = 100, cursor: str | None = None) -> Page:
        """
        Retrieves all submodel elements from a submodel.

        :param submodel: The submodel to retrieve elements from
        :param limit: Maximum number of elements to retrieve
        :param cursor: Cursor for pagination
        :return: A page containing the list of submodel elements
        :rtype: Page
        """
        submodel_id: str = submodel.id

        # Encode the submodel ID for the API
        encoded_id = to_base64_urlencoded(submodel_id)
        endpoint = f"{self.repo_url}/{encoded_id}/submodel-elements"

        try:
            logger.debug(f"Retrieving submodel elements from submodel with ID: {submodel_id}")

            # Prepare query parameters
            params: dict[str, str | int] = {'limit': limit}
            if cursor:
                params['cursor'] = cursor

            headers = self._add_auth_headers(self.default_headers)
            response = requests.get(
                url=endpoint,
                params=params,
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                json_elements = response.text
                deserialized_response = json.loads(json_elements, cls=adapter.json.AASFromJsonDecoder)
                elements = deserialized_response.get("result", [])
                cursor = deserialized_response.get("cursor")  # Extract cursor from response

                # Create a Page object with the results and cursor
                page = Page(result=elements, cursor=cursor)
                logger.debug(f"Successfully retrieved {len(elements)} submodel elements from submodel with ID: '{submodel_id}'")
                return page
            else:
                logger.warning(f"Failed to get submodel elements from submodel with ID: '{submodel_id}': {response.status_code} - {response.text}")
                return Page(result=[], cursor=None)
        except Exception as e:
            logger.warning(f"Unexpected error when retrieving submodel elements: {e}")
            return Page(result=[], cursor=None)

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

            headers = self._add_auth_headers(self.default_headers)
            response = requests.delete(
                url=endpoint,
                headers=headers,
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

    def invoke_operation(self, submodel: model.Submodel, operation_id_short_path: str, input_arguments: list | None = None, inoutput_arguments: list | None = None) -> dict[str, list[model.SubmodelElement]] | None:
        """
        Invokes an operation within a submodel synchronously.

        :param submodel: The submodel containing the operation to invoke
        :param operation_id_short_path: The idShort path of the operation to invoke (e.g., "myOperation" or "myCollection.myOperation")
        :param input_arguments: Optional dictionary of input arguments as BaSyx submodel elements for the operation
        :param inoutput_arguments: Optional dictionary of inoutput arguments as BaSyx submodel elements for the operation
        :return: The result of the operation invocation, or None if the invocation failed
        :rtype: dict | None
        """
        submodel_id: str = submodel.id

        # Encode the submodel ID for the API
        encoded_id = to_base64_urlencoded(submodel_id)
        endpoint = f"{self.repo_url}/{encoded_id}/submodel-elements/{operation_id_short_path}/invoke"

        try:
            logger.debug(f"Invoking operation '{operation_id_short_path}' in submodel with ID: {submodel_id}")

            # Prepare request data - operation variables should be BaSyx submodel elements
            operation_arguments: dict = self.input_variablify(input_arguments, inoutput_arguments)
            operation_arguments_json: str = json.dumps(operation_arguments, cls=adapter.json.AASToJsonEncoder)

            # Call the API
            headers = self._add_auth_headers(self.default_headers)
            response = requests.post(
                url=endpoint,
                data=operation_arguments_json,
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code in [200, 201]:
                response_txt = response.text if response.content else ""
                response_basyx = json.loads(response_txt, cls=adapter.json.AASFromJsonDecoder)

                result = {
                    "outputArguments": [item["value"] for item in response_basyx["outputArguments"]] if "outputArguments" in response_basyx else [],
                    "inoutputArguments": [item["value"] for item in response_basyx["inoutputArguments"]] if "inoutputArguments" in response_basyx else [],
                }

                logger.debug(f"Successfully invoked operation '{operation_id_short_path}' in submodel with ID: '{submodel_id}'")
                return result
            else:
                logger.warning(f"Failed to invoke operation '{operation_id_short_path}' in submodel with ID: '{submodel_id}': {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.warning(f"Unexpected error when invoking operation: {e}")
            return None

    def invoke_operation_async(self, submodel: model.Submodel, operation_id_short_path: str, input_arguments: list | None = None, inoutput_arguments: list | None = None) -> OperationHandle | None:
        # FIXME: This method needs to be tested and investigated whether it is implemented in the current
        # Docker component (https://hub.docker.com/r/eclipsebasyx/aas-environment) used for integration tests.
        # The async operation invocation requires the AAS environment to support the invoke-async endpoint.

        """
        Invokes an operation within a submodel asynchronously.

        :param submodel: The submodel containing the operation to invoke
        :param operation_id_short_path: The idShort path of the operation to invoke (e.g., "myOperation" or "myCollection.myOperation")
        :param input_arguments: Optional list of input arguments as BaSyx submodel elements for the operation
        :param inoutput_arguments: Optional list of inoutput arguments as BaSyx submodel elements for the operation
        :return: An OperationHandle object containing the handle ID, or None if the invocation failed
        :rtype: OperationHandle | None
        """
        submodel_id: str = submodel.id

        # Encode the submodel ID for the API
        encoded_id = to_base64_urlencoded(submodel_id)
        endpoint = f"{self.repo_url}/{encoded_id}/submodel-elements/{operation_id_short_path}/invoke-async"

        try:
            logger.debug(f"Invoking operation '{operation_id_short_path}' asynchronously in submodel with ID: {submodel_id}")

            # Prepare request data - operation variables should be BaSyx submodel elements
            operation_arguments: dict = self.input_variablify(input_arguments, inoutput_arguments)
            operation_arguments_json: str = json.dumps(operation_arguments, cls=adapter.json.AASToJsonEncoder)

            # Call the API
            headers = self._add_auth_headers(self.default_headers)
            response = requests.post(
                url=endpoint,
                data=operation_arguments_json,
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code == 202:
                # For async invocation, we get an OperationHandle with handleId
                result = response.json() if response.content else {}
                handle_id = result.get("handleId")
                if handle_id:
                    logger.debug(f"Successfully initiated async invocation of operation '{operation_id_short_path}' in submodel with ID: '{submodel_id}', handleId: {handle_id}")
                    return OperationHandle(handle_id=handle_id)
                else:
                    logger.warning(f"Failed to get handleId from async invocation response for operation '{operation_id_short_path}' in submodel with ID: '{submodel_id}'")
                    return None
            else:
                logger.warning(f"Failed to invoke operation '{operation_id_short_path}' asynchronously in submodel with ID: '{submodel_id}': {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.warning(f"Unexpected error when invoking operation asynchronously: {e}")
            return None

    def get_operation_result(self, submodel: model.Submodel, operation_id_short_path: str, handle: OperationHandle | str) -> dict | None:
        """
        Gets the result of an asynchronous operation invocation.

        :param submodel: The submodel containing the operation
        :param operation_id_short_path: The idShort path of the operation
        :param handle: The OperationHandle object or handle ID string from the async invocation
        :return: The result of the operation, or None if the operation is still running or failed
        :rtype: dict | None
        """
        submodel_id: str = submodel.id

        # Extract handle_id from OperationHandle if provided
        if isinstance(handle, OperationHandle):
            handle_id = handle.handle_id
        else:
            handle_id = handle

        # Encode the submodel ID for the API
        encoded_id = to_base64_urlencoded(submodel_id)
        # Call the GET endpoint with handleId query parameter
        endpoint = f"{self.repo_url}/{encoded_id}/submodel-elements/{operation_id_short_path}/operation?handleId={handle_id}"

        try:
            logger.debug(f"Getting result for operation '{operation_id_short_path}' with handle ID '{handle_id}' in submodel with ID: {submodel_id}")

            # Call the API
            headers = self._add_auth_headers(self.default_headers)
            response = requests.get(
                url=endpoint,
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                response_txt = response.text if response.content else ""
                result = json.loads(response_txt, cls=adapter.json.AASFromJsonDecoder) if response_txt else {}
                logger.debug(f"Successfully retrieved result for operation '{operation_id_short_path}' with handle ID '{handle_id}' in submodel with ID: '{submodel_id}'")
                return result
            elif response.status_code == 202:
                # Result not ready yet
                logger.debug(f"Result for operation '{operation_id_short_path}' with handle ID '{handle_id}' is not ready yet")
                return None
            else:
                logger.warning(f"Failed to get result for operation '{operation_id_short_path}' with handle ID '{handle_id}' in submodel with ID: '{submodel_id}': {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.warning(f"Unexpected error when getting operation result: {e}")
            return None

    def input_variablify(self, input_arguments: list | None = None, inoutput_arguments: list | None = None) -> dict:
        """
        Creates the request body for operation invocation with input and inoutput arguments.

        :param input_arguments: Dictionary of input arguments as BaSyx submodel elements
        :param inoutput_arguments: Dictionary of inoutput arguments as BaSyx submodel elements
        :return: Dictionary formatted for the API request body
        """

        return {
            "inoutputArguments": self._serialize_operation_variables(inoutput_arguments) if inoutput_arguments else [],
            "inputArguments": self._serialize_operation_variables(input_arguments) if input_arguments else [],
        }

    def output_variablify(self, output_arguments: model.SubmodelElement) -> list:
        """
        Formats a BaSyx object as operation output arguments.
        NOTE: Not spec conform, according to spec, it should look like the outcommented method below!
        This is a workaround that workes with the current version of EclipseBaSyx.

        :param basyx_object: The BaSyx object to format
        :return: List of output variables in the format expected by the API
        """
        return [
            {"value": value} for value in output_arguments
        ]

    def _serialize_operation_variables(self, variables: list) -> list:
        """
        Serializes operation variables (input_arguments, inoutput_arguments) as BaSyx submodel elements.

        :param variables: Dictionary of variable name to BaSyx submodel element mappings
        :return: List of serialized operation variables in the format expected by the API
        """
        result = []
        for value in variables:
            # Each variable is serialized as a BaSyx submodel element
            serialized = json.dumps(value, cls=adapter.json.AASToJsonEncoder)
            result.append({"value": json.loads(serialized)})
        return result

    def _deserialize_basyx_object(self, basyx_json_str: str) -> object:
        """
        Deserializes a BaSyx JSON string to a Python object.

        :param basyx_json_str: JSON string representation of a BaSyx object
        :return: Deserialized Python object
        """
        return json.loads(basyx_json_str, cls=adapter.json.AASFromJsonDecoder)

    def _serialize_basyx_object(self, basyx_obj: object) -> str:
        """
        Serializes a BaSyx object to a JSON string.

        :param basyx_obj: BaSyx object to serialize
        :return: JSON string representation
        """
        return json.dumps(basyx_obj, cls=adapter.json.AASToJsonEncoder)

    def get_parent_id(self, submodel: model.Submodel) -> str | list[str] | None:
        """
        Returns the ID or a list of IDs of the parent shell(s) if the submodel is referenced by one or more shells.

        :param submodel: The submodel to get parent ID(s) for
        :return: The parent shell ID, a list of parent shell IDs, or None if the submodel is not referenced in any shell or doesn't exist
        :rtype: str | list[str] | None
        """
        # This method requires access to AAS client functionality, which creates a circular dependency
        # The caller should provide this functionality or use a different approach
        logger.warning("get_parent_id method requires AAS client functionality which is not available due to circular import constraints")
        return None


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
                        # Single parent - AAS client functionality not available due to circular import constraints
                        logger.warning("AAS client functionality required to fetch parent shell is not available due to circular import constraints")
                        return None
                    else:
                        # Multiple parents - AAS client functionality not available due to circular import constraints
                        logger.warning("AAS client functionality required to fetch parent shells is not available due to circular import constraints")
                        return None
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
                        # TODO: Implement proper regex for "[<numeric value>]"
                        if '[' in path_parts[-1] and ']' in path_parts[-1]:
                            path_parts[-1] = path_parts[-1].split('[')[0]
                        else:
                            path_parts.pop()
                        parent_id_short_path = '.'.join(path_parts)  # Fixed join operation
                        return self.get_submodel_element(submodel, parent_id_short_path)

            elif submodel_element and not id_short_path:
                if not submodel_element.parent:
                    logger.warning("Error when retrieving parent: Could not find parent of submodelElement")
                    return None
                return submodel_element.parent

        except Exception as e:
            logger.warning(f"Unexpected error when retrieving parent: {e}")
            return None
