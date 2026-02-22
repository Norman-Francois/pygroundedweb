from __future__ import annotations

from typing import Literal

from ..base import ToolModel


class CCTag(ToolModel):
    """Configuration pour le détecteur CCTag.

    Ce modèle est utilisé pour représenter la configuration du détecteur CCTag
    côté client. Il expose le champ `resource_type` fixé à 'CCTag' afin que
    la sérialisation envoyée à l'API contienne l'information du type d'outil.

    Raises:
        pydantic.ValidationError: si les champs fournis ne respectent pas le schéma attendu.
    """
    resource_type: Literal['CCTag'] = 'CCTag'
