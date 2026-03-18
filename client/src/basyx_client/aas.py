import json
import logging

import requests
from basyx.aas import adapter, model

from basyx_client.auth import AuthType
from basyx_client.pagination import Page
from basyx_client.submodel import SubmodelClient
from basyx_client.utils import to_base64_urlencoded

logger = logging.getLogger(__name__)


class AasClient:
    def __init__(self, base_url: str, timeout: int=30, auth_type: str | AuthType | None = None, auth_credentials: tuple | None = None):
        """
        Initialize the AAS Client

        :param base_url: The base URL of the AAS repository
        :param timeout: Request timeout in seconds (default: 30)
        :param auth_type: Type of authentication ('basic' or 'token')
        :param auth_credentials: Credentials for authentication
            For basic auth: (username, password)
            For token auth: (token,)
        """
        self.repo_url = base_url + "/shells"
        self.timeout = timeout
        self.default_headers = {'Content-Type': 'application/json'}
        self.auth_type = AuthType(auth_type) if isinstance(auth_type, str) else auth_type
        self.auth_credentials = auth_credentials
        self.submodel_client = SubmodelClient(base_url, timeout)
        # Pass auth settings to submodel client
        if self.auth_type and auth_credentials:
            self.submodel_client.auth_type = self.auth_type
            self.submodel_client.auth_credentials = auth_credentials

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
            from basyx_client.auth import add_oauth2_auth, OAuth2Client
            oauth2_client: OAuth2Client = self.auth_credentials[0]
            auth_headers = add_oauth2_auth(auth_headers, oauth2_client)

        return auth_headers

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
            if self.auth_type and self.auth_credentials:
                headers = self._add_auth_headers(self.default_headers)
                response = requests.post(
                    url=self.repo_url,
                    json=json.loads(json_shell),
                    headers=headers,
                    timeout=self.timeout
                )
            else:
                response = requests.post(
                    url=self.repo_url,
                    json=json.loads(json_shell),
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
            if self.auth_type and self.auth_credentials:
                headers = self._add_auth_headers(self.default_headers)
                response = requests.put(
                    url=shell_endpoint,
                    json=json.loads(json_shell),
                    headers=headers,
                    timeout=self.timeout
                )
            else:
                response = requests.put(
                    url=shell_endpoint,
                    json=json.loads(json_shell),
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
            if self.auth_type and self.auth_credentials:
                headers = self._add_auth_headers(self.default_headers)
                response = requests.get(shell_endpoint, headers=headers, timeout=self.timeout)
            else:
                response = requests.get(shell_endpoint, timeout=self.timeout)

            if response.status_code == 200:
                shell_json = response.text
                try:
                    result = json.loads(shell_json, cls=adapter.json.AASFromJsonDecoder)
                    logger.debug(f"Successfully retrieved shell with ID: {shell_id}")
                    return result
                except Exception as e:
                    logger.warning(f"Failed to deserialize shell with AASFromJsonDecoder: {e}")
                    return None
            else:
                logger.warning(f"Failed to get shell: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.warning(f"Unexpected error when retrieving shell: {e}")
            return None

    def get_shells(self, limit: int = 100, cursor: str | None = None) -> Page:
        """
        Retrieves all Asset Administration Shells

        :param limit: Maximum number of shells to retrieve
        :param cursor: Cursor for pagination
        :return: A page containing the list of shells
        :rtype: Page
        """
        try:
            logger.debug("Retrieving all shells")

            # Prepare query parameters
            params: dict[str, str | int] = {'limit': limit}
            if cursor:
                params['cursor'] = cursor

            # Call the API
            if self.auth_type and self.auth_credentials:
                headers = self._add_auth_headers(self.default_headers)
                response = requests.get(self.repo_url, params=params, headers=headers, timeout=self.timeout)
            else:
                response = requests.get(self.repo_url, params=params, timeout=self.timeout)

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
            if self.auth_type and self.auth_credentials:
                headers = self._add_auth_headers(self.default_headers)
                response = requests.delete(shell_endpoint, headers=headers, timeout=self.timeout)
            else:
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

    def add_submodel(self, submodel: model.Submodel) -> bool:
        """
        Creates the submodel in the submodel repository and references it to this shell.

        :param submodel: The submodel to add
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            logger.debug(f"Adding submodel with ID: {submodel.id}")
            # Delegate to submodel client
            return self.submodel_client.create_submodel(submodel)
        except Exception as e:
            logger.warning(f"Unexpected error when adding submodel: {e}")
            return False

    def reference_submodel(self, shell_id: str, submodel_id: str) -> bool:
        """
        References an existing submodel in this AAS.
        NOTE: currently only implemented for ModelReferences.
        TODO: check if other reference types are valid;
            * swaggerhub api uses ExternalReference as example (https://app.swaggerhub.com/apis/Plattform_i40/AssetAdministrationShellRepositoryServiceSpecification/V3.0.1_SSP-001#/Asset%20Administration%20Shell%20Repository%20API/PostSubmodelReference_AasRepository)
            * SPOT AAS only defines ModelReference (https://industrialdigitaltwin.io/aas-specifications/IDTA-01001/v3.1.2/spec-metamodel/core.html#aas_attributes)

        NOTE: we are retreiving the submodel references from from a shell, instead of using the GET `/shells/{aasIdentifier}/submodel-refs` endpoint to avoid pagination handling
        :param shell_id: The ID of the AAS to reference the submodel in
        :param submodel_id: The ID of the submodel to reference
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            submodel_ref = self._create_model_ref(submodel_id)
            logger.debug(f"Referencing submodel with ID: {submodel_id} in shell: {shell_id}")

            # Encode the shell ID for the API
            encoded_shell_id = to_base64_urlencoded(shell_id)
            shell_endpoint = f"{self.repo_url}/{encoded_shell_id}/submodel-refs"

            # Create the submodel reference payload
            submodel_ref_payload = json.dumps(submodel_ref, cls=adapter.json.AASToJsonEncoder)

            # Call the API
            if self.auth_type and self.auth_credentials:
                headers = self._add_auth_headers(self.default_headers)
                headers['Content-Type'] = 'application/json'
                response = requests.post(
                    url=shell_endpoint,
                    data=submodel_ref_payload,
                    headers=headers,
                    timeout=self.timeout
                )
            else:
                headers = {'Content-Type': 'application/json'}
                response = requests.post(
                    url=shell_endpoint,
                    data=submodel_ref_payload,
                    headers=headers,
                    timeout=self.timeout
                )

            if response.status_code == 201:
                logger.debug(f"Successfully referenced submodel with ID: {submodel_id} in shell: {shell_id}")
                return True
            else:
                logger.warning(f"Failed to reference submodel: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.warning(f"Unexpected error when referencing submodel: {e}")
            return False

    def _create_model_ref(self, referable_id: str) -> model.ModelReference:
        # Create a dummy submodel with the actual submodel_id
        dummy_submodel: model.Submodel = model.Submodel(id_=referable_id, id_short="dummy")
        return model.ModelReference.from_referable(dummy_submodel)

    def get_submodel_references(self, shell_id: str) -> list[model.ModelReference] | None:
        """
        Retrieves all submodel references associated with this AAS.

        :param shell_id: The ID of the AAS to retrieve submodel references for
        :return: A list of submodel references, or None if not found
        :rtype: list[model.ModelReference] | None
        """
        shell: model.AssetAdministrationShell = self.get_shell(shell_id)
        if shell:
            logger.debug(f"Retrieving submodel references for shell: {shell_id}")

            # in basyx_python_sdk submodel references are located in AssetAdministrationShell.submodel
            return shell.submodel
        return None


    def get_submodels(self, shell_id: str) -> list[model.Submodel]:
        """
        Retrieves all submodels referenced by this shell.

        :param shell_id: The ID of the shell to retrieve submodels for
        :return: A list of submodels, or [] if not found
        :rtype: list[model.Submodel]
        """
        try:
            submodel_refs = self.get_submodel_references(shell_id)
            if not submodel_refs:
                logger.debug(f"No submodel references found for shell: {shell_id}")
                return []

            logger.debug(f"Retrieving submodels for shell: {shell_id}")
            submodels: list[model.Submodel] = []
            for ref in submodel_refs:
                if not isinstance(ref, model.ModelReference):
                    logger.warning(f"Failed to retrieve submodel for reference: '{ref}'\nHint: Submodel references should be of Type ModelReference")
                    continue
                submodel_id = ref.key[0].value
                submodel = self.submodel_client.get_submodel(submodel_id)
                if submodel is not None:
                    submodels.append(submodel)
            return submodels
        except Exception as e:
            logger.warning(f"Unexpected error when retrieving submodels: {e}")
            return []


    def remove_submodel(self, shell_id: str, submodel_id: str, delete_submodel: bool = False) -> bool:
        """
        Removes a submodel reference from the shell.
        If delete_submodel is True, the submodel will be deleted from the submodel repository as well.

        :param shell_id: The ID of the shell to remove the submodel from
        :param submodel_id: The ID of the submodel to remove
        :param delete_submodel: If True, also delete the submodel from the submodel repository
        :return: True if submodel could be removed, False if not (e.g. if ID was not available)
        :rtype: bool
        """
        try:
            logger.debug(f"Removing submodel reference with ID: {submodel_id} from shell: {shell_id}")

            # Encode the IDs for the API
            encoded_shell_id = to_base64_urlencoded(shell_id)
            encoded_submodel_id = to_base64_urlencoded(submodel_id)
            shell_endpoint = f"{self.repo_url}/{encoded_shell_id}/submodel-refs/{encoded_submodel_id}"

            # Call the API to remove the submodel reference
            if self.auth_type and self.auth_credentials:
                headers = self._add_auth_headers(self.default_headers)
                response = requests.delete(shell_endpoint, headers=headers, timeout=self.timeout)
            else:
                response = requests.delete(shell_endpoint, timeout=self.timeout)

            success = False
            if response.status_code == 204:
                logger.debug(f"Successfully removed submodel reference with ID: {submodel_id} from shell: {shell_id}")
                success = True
            else:
                logger.warning(f"Failed to remove submodel reference: {response.status_code} - {response.text}")
                return False

            # If delete_submodel is True, also delete the submodel from the submodel repository
            if delete_submodel and success:
                logger.debug(f"Deleting submodel with ID: {submodel_id} from submodel repository")
                submodel_deleted = self.submodel_client.delete_submodel(submodel_id)
                if not submodel_deleted:
                    logger.warning(f"Failed to delete submodel with ID: {submodel_id} from submodel repository")
                    return False

            return success
        except Exception as e:
            logger.warning(f"Unexpected error when removing submodel: {e}")
            return False
