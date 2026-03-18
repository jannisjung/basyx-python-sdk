"""
Authentication utilities for the BaSyx client.
This module provides utility functions for adding authentication to API calls.
"""

import base64
import time
import urllib.parse
from enum import Enum
from typing import Optional, Any
import requests


class AuthType(Enum):
    BASIC = "basic"
    TOKEN = "token"
    OAUTH2 = "oauth2"


class OAuth2Client:
    """
    OAuth2 client for handling OAuth2 authentication flows.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        authorization_url: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        scope: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize OAuth2 client.

        :param client_id: OAuth2 client ID
        :param client_secret: OAuth2 client secret
        :param token_url: URL for obtaining tokens
        :param authorization_url: URL for authorization (optional, for authorization code flow)
        :param redirect_uri: Redirect URI (optional, for authorization code flow)
        :param scope: Scope for the authorization (optional)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.authorization_url = authorization_url
        self.redirect_uri = redirect_uri
        self.scope = scope

        # Token storage
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.expires_at: Optional[float] = None
        self.token_data: dict[str, Any] = {}

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate the authorization URL for the authorization code flow.

        :param state: State parameter for security
        :return: Authorization URL
        """
        if not self.authorization_url:
            raise ValueError("Authorization URL not configured")

        params = {
            'response_type': 'code',
            'client_id': self.client_id,
        }

        if self.redirect_uri:
            params['redirect_uri'] = self.redirect_uri

        if self.scope:
            params['scope'] = self.scope

        if state:
            params['state'] = state

        query_string = urllib.parse.urlencode(params)
        return f"{self.authorization_url}?{query_string}"

    def fetch_token(self, code: Optional[str] = None, grant_type: str = 'authorization_code') -> dict[str, Any]:
        """
        Fetch an access token using the authorization code or refresh token.

        :param code: Authorization code (for authorization_code grant)
        :param grant_type: Grant type (authorization_code or refresh_token)
        :return: Token data
        """
        data = {
            'grant_type': grant_type,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        if grant_type == 'authorization_code':
            if not code:
                raise ValueError("Authorization code required for authorization_code grant")
            data['code'] = code
            if self.redirect_uri:
                data['redirect_uri'] = self.redirect_uri
        elif grant_type == 'refresh_token':
            if not self.refresh_token:
                raise ValueError("Refresh token not available")
            data['refresh_token'] = self.refresh_token
        else:
            raise ValueError(f"Unsupported grant type: {grant_type}")

        response = requests.post(self.token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data.get('access_token')
        self.refresh_token = token_data.get('refresh_token', self.refresh_token)

        expires_in = token_data.get('expires_in', 3600)
        self.expires_at = time.time() + expires_in - 60  # Refresh 1 minute early

        self.token_data = token_data
        return token_data

    def refresh_access_token(self) -> dict[str, Any]:
        """
        Refresh the access token using the refresh token.

        :return: New token data
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        return self.fetch_token(grant_type='refresh_token')

    def is_token_expired(self) -> bool:
        """
        Check if the access token is expired or will expire soon.

        :return: True if token is expired, False otherwise
        """
        if not self.expires_at:
            return True
        return time.time() >= self.expires_at

    def get_valid_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.

        :return: Valid access token
        """
        if not self.access_token or self.is_token_expired():
            if self.refresh_token:
                try:
                    self.refresh_access_token()
                except Exception:
                    # If refresh fails, we'll need to re-authenticate
                    pass
            if not self.access_token:
                raise ValueError("No valid access token available. Please authenticate.")

        return self.access_token

    def authenticate_password(self, username: str, password: str) -> dict[str, Any]:
        """
        Authenticate using the Resource Owner Password Credentials flow.

        :param username: User's username
        :param password: User's password
        :return: Token data
        """
        data = {
            'grant_type': 'password',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': username,
            'password': password,
        }

        if self.scope:
            data['scope'] = self.scope

        response = requests.post(self.token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data.get('access_token')
        self.refresh_token = token_data.get('refresh_token')

        expires_in = token_data.get('expires_in', 3600)
        self.expires_at = time.time() + expires_in - 60  # Refresh 1 minute early

        self.token_data = token_data
        return token_data

    def authenticate_client_credentials(self) -> dict[str, Any]:
        """
        Authenticate using the Client Credentials flow.

        :return: Token data
        """
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        if self.scope:
            data['scope'] = self.scope

        response = requests.post(self.token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data.get('access_token')
        self.expires_at = time.time() + token_data.get('expires_in', 3600) - 60  # Refresh 1 minute early

        self.token_data = token_data
        return token_data


def add_basic_auth(headers: dict, username: str, password: str) -> dict:
    """
    Add Basic Authentication to headers.

    :param headers: dictionary of headers to add authentication to
    :param username: Username for basic authentication
    :param password: Password for basic authentication
    :return: Updated headers dictionary
    """
    credentials = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('ascii')
    headers['Authorization'] = f"Basic {credentials}"
    return headers


def add_token_auth(headers: dict, token: str) -> dict:
    """
    Add Token Authentication to headers.

    :param headers: dictionary of headers to add authentication to
    :param token: Token for authentication
    :return: Updated headers dictionary
    """
    headers['Authorization'] = f"Bearer {token}"
    return headers


def add_oauth2_auth(headers: dict, oauth2_client: OAuth2Client) -> dict:
    """
    Add OAuth2 Authentication to headers.

    :param headers: dictionary of headers to add authentication to
    :param oauth2_client: OAuth2Client instance
    :return: Updated headers dictionary
    """
    token = oauth2_client.get_valid_token()
    headers['Authorization'] = f"Bearer {token}"
    return headers
