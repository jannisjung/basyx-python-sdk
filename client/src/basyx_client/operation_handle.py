from dataclasses import dataclass


@dataclass
class OperationHandle:
    """
    Represents a handle for an asynchronous operation invocation.

    :param handle_id: The unique identifier for the operation handle
    """
    handle_id: str
