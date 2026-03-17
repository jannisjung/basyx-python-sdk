"""
Authentication utilities for the BaSyx client.
This module provides utility functions for adding authentication to API calls.
"""

import base64
from enum import Enum


class AuthType(Enum):
    BASIC = "basic"
    TOKEN = "token"


def add_basic_auth(headers: dict, username: str, password: str) -> dict:
    """
    Add Basic Authentication to headers.

    :param headers: Dictionary of headers to add authentication to
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

    :param headers: Dictionary of headers to add authentication to
    :param token: Token for authentication
    :return: Updated headers dictionary
    """
    headers['Authorization'] = f"Bearer {token}"
    return headers
