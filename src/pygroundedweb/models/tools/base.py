from __future__ import annotations

from typing import Dict, Any

from pygroundedweb.models.base import APIModel


class ToolModel(APIModel):
    """Base pour les modèles de configuration d'outils (detector, sfm, cloud_processor).

    Les sous-classes définissent un champ `resource_type` (Literal) permettant au serveur
    de reconnaître le type d'outil lors de la sérialisation.

    Raises:
        pydantic.ValidationError: si la construction du modèle échoue.
    """

    # Déclaré ici pour satisfaire les analyseurs statiques ; les sous-classes
    # doivent redéfinir cette valeur avec un Literal approprié.
    resource_type: str = ""

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Sérialise le modèle en dict et injecte le champ `resource_type`.

        Returns:
            dict: dictionnaire sérialisé contenant au minimum les champs du modèle
                  et la clé `resource_type`.
        """
        data = super().model_dump(**kwargs)
        data["resource_type"] = getattr(self, "resource_type", "")
        return data
