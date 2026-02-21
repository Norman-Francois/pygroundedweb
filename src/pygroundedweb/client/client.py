"""Facade client qui regroupe les clients spécifiques par ressource.

Fournit un accès simple aux sous-clients : dataset, analysis, configuration, et des méthodes
pour l'authentification (login/logout) et l'accès à l'utilisateur courant.
"""

from typing import Optional

from .base import BaseAPIClient
from .configuration import ConfigurationClient
from .dataset import DatasetClient
from .analysis import AnalysisClient
from ..models.user import User


class GroundedWebClient:
    """Client principal à utiliser par les consommateurs de la bibliothèque.

    Exemple d'utilisation :
        client = GroundedWebClient("http://example.com")
        client.login(email, password)
        ds = client.dataset.create("Mon dataset", photos_before=["a.jpg"])

    Attributs exposés :
        dataset: DatasetClient
        analysis: AnalysisClient
        configuration: ConfigurationClient
    """
    def __init__(self, base_url: str, check_connection: bool = True):
        self._api = BaseAPIClient(base_url, check_connection=check_connection)
        self.dataset = DatasetClient(self._api)
        self.analysis = AnalysisClient(self._api)
        self.configuration = ConfigurationClient(self._api)

    def login(self, email: str, password: str):
        """Authentifie l'utilisateur auprès de l'API.

        Args:
            email: adresse email.
            password: mot de passe en clair.
        """
        self._api.login(email, password)

    def logout(self):
        """Déconnecte la session courante et nettoie les cookies locaux."""
        self._api.logout()

    @property
    def is_authenticated(self) -> bool:
        """Indique si la session courante est authentifiée."""
        return self._api.is_authenticated

    @property
    def current_user(self) -> Optional[User]:
        """Retourne l'objet `User` courant si authentifié, sinon None."""
        return self._api.current_user