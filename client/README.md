# Eclipse BaSyx Python Client SDK

> **Important notes:**
> - The client SDK is currently a Work in Progress (WIP).
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

Note: The following usage sections are placeholders since the SDK is currently a WIP and a final API is not yet established.

- AASX functions:
- `upload_aasx` – Upload all AASX files, recursively found in a given directory, or a single AASX file.
- `download_aasx` – Download the entire repository as an AASX, or as an AASX file per shell; optionally download specific shells by id, with options to include/exclude submodels; or download just one or more submodels by id with a carrier shell around them.

- AAS functions:
- `create_shell`
- `update_shell`
- `get_shell`
- `get_shells`
- `delete_shell`
- `add_submodel` – Creates the submodel in the submodel repository and references it to this shell
- `reference_submodel` – References an existing submodel
- `remove_submodel_reference`
- `get_submodel_references`
- `get_submodels`
- `delete_submodel` – Removes the reference from the shell and deletes the submodel from the submodel repository

- Submodel functions:
- `create_submodel`
- `update_submodel`
- `delete_submodel`
- `add_submodel_element`
- `update_submodel_element`
- `update_submodel_element_value`
- `delete_submodel_element`
- `get_patent:_id` – For submodels, returns the parent_aas_id; for submodel elements, returns either the submodel_id, or for nested submodel elements, returns the submodel_id with the path to the submodel
- `get_parent` – For submodels, returns the parent_aas; for submodel elements, returns either the submodel or, for nested submodel elements, returns the parent submodel_element_collection or submodel_element_list

> Note: The above descriptions are placeholders since the SDK is still a WIP. Please adjust API method names and descriptions to your final implementation.

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
- [ ] 
- [ ] add_submodel
- [ ] reference_submodel

- [ ] get_submodel_references
- [ ] get_submodels
- [ ] remove_submodel

#### Submodel Functions

- [ ] create_submodel
- [ ] update_submodel

- [ ] delete_submodel
- [ ] add_submodel_element

- [ ] update_submodel_element
- [ ] update_submodel_element_value

- [ ] delete_submodel_element
- [ ] get_parent_id

- [ ] get_parent


### License
`MIT`

