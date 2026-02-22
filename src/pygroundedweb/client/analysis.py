"""Client pour gérer les analyses (création, lecture, mise à jour, suppression).

Fournit des helpers pour créer une analyse à partir d'une configuration et d'un dataset.
"""

from typing import Optional, List

from .base import APIModelClient
from ..models.analysis import Analysis
from ..models.configuration import Configuration
from ..models.dataset import Dataset


class AnalysisClient(APIModelClient):
    """Client CRUD pour les ressources `Analysis` côté API.

    Les méthodes exposées effectuent les appels réseau via `BaseAPIClient` et
    peuvent propager `APIError`, `NetworkError`, `PermissionDenied` ou
    `pydantic.ValidationError` en cas d'erreur.
    """

    def _parse_json(self, analysis_json: str) -> Analysis:
        """Convertit le JSON renvoyé par l'API en instance `Analysis` et attache le client."""
        instance = Analysis.model_validate(analysis_json)
        object.__setattr__(instance, "_client", self)
        return instance

    def create(
            self,
            analysis_name: str,
            configuration: Configuration,
            dataset: Optional[Dataset] = None,
            dataset_id: Optional[int] = None,
            selected_photos_id: Optional[List[int]] = None,
            notify_by_email: Optional[bool] = False,
    ) -> Analysis:
        """Crée une analyse côté API.

        Args:
            analysis_name: nom de l'analyse.
            configuration: instance de `Configuration` à utiliser.
            dataset: (optionnel) instance de `Dataset`.
            dataset_id: (optionnel) identifiant du dataset (alternative à dataset).
            selected_photos_id: liste d'IDs de photos sélectionnées pour l'analyse.
            notify_by_email: si True, le serveur enverra une notification par e-mail en fin de traitement.

        Returns:
            Instance `Analysis` correspondant à la ressource créée.

        Raises:
            ValueError: si ni dataset ni dataset_id ne sont fournis ou si les deux le sont.
            APIError, NetworkError, PermissionDenied, pydantic.ValidationError
        """

        if not ((dataset is None) ^ (dataset_id is None)):
            raise ValueError("You must provide either 'dataset' or 'dataset_id', but not both.")

        if dataset is not None:
            dataset_id = dataset.pk

        data_analysis = {
            "name": analysis_name,
            "notify_by_email": notify_by_email,
            "configuration": configuration.model_dump(),
            "selection": {
                "dataset_id": dataset_id,
                **({"photos_ids": selected_photos_id} if selected_photos_id is not None else {})
            }
        }

        analysis_json = self._client.create("analyzes", data_analysis)
        analysis_json["mutable_fields"] = ["name", "notify_by_email"]
        return self._parse_json(analysis_json)

    def retrieve(self, analysis_id: int):
        """Récupère une analyse par son identifiant et renvoie une instance `Analysis`.

        Raises:
            APIError, NetworkError, PermissionDenied, pydantic.ValidationError
        """
        analysis_json = self._client.get_by_id("analyzes", analysis_id)
        analysis_json["mutable_fields"] = ["name", "notify_by_email"]
        return self._parse_json(analysis_json)

    def update(self, analysis: Analysis) -> Analysis:
        """Met à jour une analyse existante et retourne l'objet mis à jour.

        Raises:
            APIError, NetworkError, PermissionDenied, pydantic.ValidationError
        """
        analysis_json = self._client.update("analyzes", analysis)
        analysis_json["mutable_fields"] = ["name", "notify_by_email"]
        return self._parse_json(analysis_json)

    def delete(self, analysis_id: int):
        """Supprime une analyse par identifiant.

        Raises:
            APIError, NetworkError, PermissionDenied
        """
        self._client.delete_by_id("analyzes", analysis_id)