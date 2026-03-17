"""
Example usage of authentication features in the BaSyx client.
"""

# Example 1: Using Basic Authentication
from basyx_client.aas import AasClient

# Create client with basic authentication
aas_client = AasClient(
    base_url="http://localhost:8080",
    auth_type="basic",
    auth_credentials=("username", "password")
)

# All API calls will now include Basic Authentication headers
# aas_client.create_shell(shell)


# Example 2: Using Token Authentication
from basyx_client.submodel import SubmodelClient

# Create client with token authentication
submodel_client = SubmodelClient(base_url="http://localhost:8080")
submodel_client.auth_type = "token"
submodel_client.auth_credentials = ("your-token-here",)

# All API calls will now include Bearer Token Authentication headers
# submodel_client.create_submodel(submodel)


# Example 3: Adding authentication after client creation
aas_client2 = AasClient(base_url="http://localhost:8080")

# Add basic authentication later
aas_client2.auth_type = "basic"
aas_client2.auth_credentials = ("username", "password")

# Or add token authentication later
# aas_client2.auth_type = "token"
# aas_client2.auth_credentials = ("your-token-here",)