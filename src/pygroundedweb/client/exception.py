"""Exceptions personnalisées levées par le client HTTP.

Ces exceptions permettent de différencier :
- les erreurs réseau réessayables (NetworkError),
- les refus d'autorisation (PermissionDenied),
- les erreurs API retournées par le serveur (APIError),
- les erreurs liées à l'upload de fichiers (UploadError).
"""

class NetworkError(Exception):
    """Erreur liée à un échec réseau ou à une réponse 5xx de l'API."""
    pass

class PermissionDenied(Exception):
    """Erreur indiquant que l'opération est interdite (401/403)."""
    pass

class APIError(Exception):
    """Erreur générique représentant une réponse d'erreur de l'API."""
    pass

class UploadError(Exception):
    """Erreur signalant l'échec d'un (ou plusieurs) upload(s) de fichier(s)."""
    pass