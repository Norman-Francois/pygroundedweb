from __future__ import annotations

from typing import Dict, Any

from pygroundedweb.models.base import APIModel


class ToolModel(APIModel):

    @property
    def resource_type(self) -> str:
        return self.__class__.__name__

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        data = super().model_dump(**kwargs)
        data["resource_type"] = self.resource_type
        return data
