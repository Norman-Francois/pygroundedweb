from __future__ import annotations

from typing import List, Optional

from .base import APIModel
from .scalebar import ScaleBar
from .tools.cloud_processor.base import CloudProcessor
from .tools.detector.base import Detector
from .tools.sfm.base import SFM


class Configuration(APIModel):
    name: str
    scale_bars: List[ScaleBar]
    detector: Detector
    cloud_processor: CloudProcessor
    sfm: SFM
    display_padding: Optional[bool] = None

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data["detector"] = self.detector.model_dump(**kwargs)
        data["cloud_processor"] = self.cloud_processor.model_dump(**kwargs)
        data["sfm"] = self.sfm.model_dump(**kwargs)

        if self.display_padding is not None:
            data["display_padding"] = self.display_padding
        else:
            data.pop("display_padding")

        return data
