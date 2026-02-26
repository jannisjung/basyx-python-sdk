import base64


def to_base64_urlencoded(input_str: str) -> str:
    encoded_bytes = base64.urlsafe_b64encode(input_str.encode('utf-8'))
    encoded_str = encoded_bytes.decode('utf-8')
    return encoded_str.rstrip('=')
