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

