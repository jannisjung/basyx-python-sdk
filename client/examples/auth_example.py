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


# Example 4: Using OAuth2 Authentication
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

# Method 1: Client Credentials Flow (for service-to-service authentication)
# oauth2_client.authenticate_client_credentials()

# Method 2: Resource Owner Password Credentials Flow (for user authentication)
# oauth2_client.authenticate_password("username", "password")

# Method 3: Authorization Code Flow (for user authentication with redirect)
# 1. Get authorization URL
# auth_url = oauth2_client.get_authorization_url(state="random_state_string")
# print(f"Visit this URL to authorize: {auth_url}")
#
# 2. After user authorizes, they will be redirected to your redirect_uri with a code
# 3. Exchange the code for tokens
# oauth2_client.fetch_token(code="authorization_code_from_callback")

# Create client with OAuth2 authentication
aas_client3 = AasClient(
    base_url="http://localhost:8080",
    auth_type="oauth2",
    auth_credentials=(oauth2_client,)
)

# All API calls will now include OAuth2 Bearer Token Authentication headers
# The client will automatically refresh tokens when needed
# aas_client3.create_shell(shell)
