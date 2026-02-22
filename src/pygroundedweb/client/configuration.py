from typing import List

from .base import APIModelClient
from ..models.configuration import Configuration


class ConfigurationClient(APIModelClient):
    """Client CRUD pour les configurations d'analyse.

    Fournit les opérations de création, lecture, mise à jour, suppression et
    liste des `Configuration` côté API.

    Les méthodes peuvent lever des exceptions liées aux appels HTTP ou à la
    validation des modèles côté client.
    """

    def _parse_json(self, config_json: dict) -> Configuration:
        config_json["mutable_fields"] = ["name", "scale_bars", "detector", "cloud_processor", "sfm",
                                         "display_padding"]
        instance = Configuration.model_validate(config_json)
        object.__setattr__(instance, "_client", self)
        return instance

    def create(self, configuration: Configuration) -> Configuration:
        """Crée une configuration côté API.

        Args:
            configuration: instance `Configuration` à envoyer.

        Returns:
            L'instance `Configuration` créée telle que renvoyée par l'API.

        Raises:
            APIError: si l'API retourne une erreur lors de la création.
            NetworkError: en cas de problème réseau persistant.
            PermissionDenied: si les droits sont insuffisants.
            pydantic.ValidationError: si la validation du modèle côté client échoue.
        """
        data = configuration.model_dump()
        config_json = self._client.create("configurations", data)
        return self._parse_json(config_json)

    def retrieve(self, config_id: int) -> Configuration:
        """Récupère une configuration par son identifiant.

        Args:
            config_id: identifiant numérique de la configuration.

        Returns:
            Instance `Configuration` correspondant à la ressource distante.

        Raises:
            APIError: si l'API retourne une erreur.
            NetworkError: en cas de problème réseau.
            PermissionDenied: si l'accès est interdit.
            pydantic.ValidationError: si la réponse ne peut être validée en `Configuration`.
        """
        config_json = self._client.get_by_id("configurations", config_id)
        return self._parse_json(config_json)

    def update(self, configuration: Configuration) -> Configuration:
        """Met à jour une configuration existante.

        Args:
            configuration: instance `Configuration` contenant les modifications.

        Returns:
            Instance `Configuration` mise à jour.

        Raises:
            APIError, NetworkError, PermissionDenied, pydantic.ValidationError
        """
        config_json = self._client.update("configurations", configuration)
        return self._parse_json(config_json)

    def delete(self, config_id: int) -> None:
        """Supprime une configuration par identifiant.

        Raises:
            APIError, NetworkError, PermissionDenied
        """
        self._client.delete_by_id("configurations", config_id)

    def list(self) -> List[Configuration]:
        """Liste toutes les configurations disponibles côté API.

        Returns:
            Liste d'instances `Configuration`.

        Raises:
            APIError, NetworkError, PermissionDenied, pydantic.ValidationError
        """
        configs_data = self._client.get_all("configurations")
        return [self._parse_json(c) for c in configs_data]