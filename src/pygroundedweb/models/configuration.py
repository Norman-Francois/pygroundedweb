"""Modèle de configuration d'analyse et utilitaires de sérialisation.

Ce modèle inclut les sous-modèles pour les detecteurs, cloud-processor et SFM.
"""

from __future__ import annotations

from typing import List, Optional

from .base import APIModel
from .scalebar import ScaleBar
from .tools.cloud_processor import CloudProcessor
from .tools.detector import Detector
from .tools.sfm import SFM


class Configuration(APIModel):
    """Configuration complète utilisée pour lancer une analyse.

    Champs:
        name: nom optionnel de la configuration.
        scale_bars: liste de ScaleBar.
        detector: configuration du détecteur.
        cloud_processor: configuration du traitement du nuage.
        sfm: configuration SFM.
        display_padding: option d'affichage facultative.
    """
    name: Optional[str] = None
    scale_bars: List[ScaleBar]
    detector: Detector
    cloud_processor: CloudProcessor
    sfm: SFM
    display_padding: Optional[bool] = None

    def model_dump(self, **kwargs):
        """Sérialise le modèle en dict en appliquant une logique pour les sous-modèles.

        Cette méthode garantit que `detector`, `cloud_processor` et `sfm` sont eux-mêmes
        sérialisés via leur `model_dump` avant d'être envoyés à l'API.
        """
        data = super().model_dump(**kwargs)
        data["detector"] = self.detector.model_dump(**kwargs)
        data["cloud_processor"] = self.cloud_processor.model_dump(**kwargs)
        data["sfm"] = self.sfm.model_dump(**kwargs)

        if self.display_padding is not None:
            data["display_padding"] = self.display_padding
        else:
            data.pop("display_padding")

        return data
