# Eclipse BaSyx Python Client SDK

> **Important notes:**
> - The client SDK is now feature-complete for basic AAS and Submodel operations.
> - In other projects, reference in your `requirements.txt`:
>
>    ```
>    git+https://github.com/jannisjung/basyx-python-sdk.git@feature/client-sdk#subdirectory=client
>    ```

## Contents
- [Eclipse BaSyx Python Client SDK](#eclipse-basyx-python-client-sdk)
  - [Contents](#contents)
  - [Installation](#installation)
    - [For Developers of this feature](#for-developers-of-this-feature)
    - [For Users in Projects](#for-users-in-projects)
  - [Usage](#usage)
    - [Authentication](#authentication)
      - [OAuth2 Authentication](#oauth2-authentication)
    - [Development Coverage (TODO)](#development-coverage-todo)
      - [AASX](#aasx)
      - [AAS Functions](#aas-functions)
      - [Submodel Functions](#submodel-functions)
    - [License](#license)

## Installation

### For Developers of this feature
1. Clone the repository.
2. Install development dependencies:
3. navigate to [`client`](.) 
4. `pip install -e .`

### For Users in Projects

You can integrate this SDK into your project via the pyproject.toml configuration or by using the Git URL as shown above.

## Usage

The client SDK provides a comprehensive set of functions for interacting with Eclipse BaSyx servers:

- AASX functions:
- (Not yet implemented) – AASX functionality is planned but not yet implemented in the current version.

- AAS functions:
- `create_shell` – Creates a new Asset Administration Shell
- `update_shell` – Updates an existing Asset Administration Shell
- `get_shell` – Retrieves a specific Asset Administration Shell by ID
- `get_shells` – Retrieves all Asset Administration Shells with pagination support
- `delete_shell` – Deletes an Asset Administration Shell
- `add_submodel` – Creates the submodel in the submodel repository and references it to this shell
- `reference_submodel` – References an existing submodel in this AAS
- `remove_submodel` – Removes a submodel reference from the shell and optionally deletes the submodel from the submodel repository
- `get_submodel_references` – Retrieves all submodel references associated with this AAS
- `get_submodels` – Retrieves all submodels referenced by this shell

- Submodel functions:
- `create_submodel` – Creates a new Submodel
- `update_submodel` – Updates an existing Submodel
- `delete_submodel` – Deletes a Submodel
- `add_submodel_element` – Adds a new submodel element to the given submodel at the specified id_short_path
- `update_submodel_element` – Updates an existing submodel element within a submodel
- `update_submodel_element_value` – Updates the value of an existing submodel element
- `delete_submodel_element` – Deletes a submodel element from the given submodel
- `get_submodel_element` – Retrieves a specific submodel element by its idShort path
- `get_submodel_elements` – Retrieves all submodel elements from a submodel
- `get_parent_id` – Returns the ID or a list of IDs of the parent shell(s) if the submodel is referenced by one or more shells
- `get_parent` – Returns the parent object of a submodel or submodel element
- `invoke_operation` – Invokes an operation within a submodel synchronously
- `invoke_operation_async` – Invokes an operation within a submodel asynchronously
- `get_operation_result` – Gets the result of an asynchronous operation invocation

### Authentication

The client SDK now supports Basic Authentication, Token Authentication, and OAuth2 for securing API calls:

- **Basic Authentication**: Username and password based authentication
- **Token Authentication**: Bearer token based authentication
- **OAuth2 Authentication**: Industry-standard protocol for authorization

To use authentication, you can either:

1. Initialize the client with authentication credentials:
   ```python
   from basyx_client.aas import AasClient
   
   # Basic Authentication
   aas_client = AasClient(
       base_url="http://localhost:8080",
       auth_type="basic",
       auth_credentials=("username", "password")
   )
   
   # Token Authentication
   aas_client = AasClient(
       base_url="http://localhost:8080",
       auth_type="token",
       auth_credentials=("your-token-here",)
   )
   ```

2. Set authentication after client creation:
   ```python
   from basyx_client.submodel import SubmodelClient
   
   submodel_client = SubmodelClient(base_url="http://localhost:8080")
   
   # Add basic authentication
   submodel_client.auth_type = "basic"
   submodel_client.auth_credentials = ("username", "password")
   
   # Or add token authentication
   submodel_client.auth_type = "token"
   submodel_client.auth_credentials = ("your-token-here",)
   ```

#### OAuth2 Authentication

The SDK provides comprehensive OAuth2 support with automatic token refresh capabilities. OAuth2 is the recommended authentication method for production applications.

```python
from basyx_client.aas import AasClient
from basyx_client.auth import OAuth2Client

# Create OAuth2 client
oauth2_client = OAuth2Client(
    client_id="your_client_id",
    client_secret="your_client_secret",
    token_url="https://your-oauth-provider.com/oauth/token",
    authorization_url="https://your-oauth-provider.com/oauth/authorize",  # Optional, for authorization code flow
    redirect_uri="http://localhost:8080/callback",  # Optional, for authorization code flow
    scope="read write"  # Optional
)

# Method 1: Client Credentials Flow (service-to-service)
oauth2_client.authenticate_client_credentials()

# Method 2: Resource Owner Password Credentials Flow (user authentication)
# oauth2_client.authenticate_password("username", "password")

# Method 3: Authorization Code Flow (user authentication with redirect)
# 1. Get authorization URL
# auth_url = oauth2_client.get_authorization_url(state="random_state_string")
# print(f"Visit this URL to authorize: {auth_url}")
# 
# 2. After user authorizes, they will be redirected with a code
# 3. Exchange the code for tokens
# oauth2_client.fetch_token(code="authorization_code_from_callback")

# Create client with OAuth2 authentication
aas_client = AasClient(
    base_url="http://localhost:8080",
    auth_type="oauth2",
    auth_credentials=(oauth2_client,)
)

# All API calls will automatically include OAuth2 Bearer Token Authentication headers
# The client will automatically refresh tokens when needed
```

Supported OAuth2 flows:
- **Client Credentials Flow**: Service-to-service authentication
- **Resource Owner Password Credentials Flow**: Direct user credential exchange
- **Authorization Code Flow**: Standard web server flow with redirect

The OAuth2 implementation includes automatic token refresh, so your application won't lose connectivity when tokens expire.

All API calls made through the authenticated client will automatically include the appropriate authentication headers.

> Note: The above descriptions reflect the current implementation status of the SDK.

### Development Coverage (TODO)

#### AASX

- [ ] upload_aasx
- [ ] download_aasx

#### AAS Functions

- [x] create_shell
- [x] update_shell

- [x] get_shell
- [x] get_shells

- [x] delete_shell
- [x] add_submodel
- [x] reference_submodel

- [x] get_submodel_references
- [x] get_submodels
- [x] remove_submodel

#### Submodel Functions

- [x] create_submodel
- [x] update_submodel

- [x] delete_submodel
- [x] add_submodel_element

- [x] update_submodel_element
- [x] update_submodel_element_value

- [x] delete_submodel_element
- [x] get_parent_id

- [x] get_parent


### License
`MIT`

