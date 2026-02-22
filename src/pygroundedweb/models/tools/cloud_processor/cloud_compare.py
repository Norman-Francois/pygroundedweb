from __future__ import annotations

from typing import Literal

from ..base import ToolModel


class CloudCompare(ToolModel):
    """Configuration pour le cloud-processor CloudCompare.

    Représente la configuration minimale nécessaire pour utiliser CloudCompare
    comme étape de post-traitement des nuages de points. Le champ
    `resource_type` est ajouté automatiquement lors de la sérialisation.

    Raises:
        pydantic.ValidationError: si la construction du modèle échoue.
    """
    resource_type: Literal['CloudCompare'] = 'CloudCompare'
