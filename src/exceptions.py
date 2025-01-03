class NebulaError(Exception):
    """Base exception for all Nebula-related errors."""

class NebulaAPIError(NebulaError):
    """Raised when the Nebula API returns an error."""

