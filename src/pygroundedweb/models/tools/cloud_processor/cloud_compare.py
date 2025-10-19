from __future__ import annotations

from typing import Literal

from ..base import ToolModel


class CloudCompare(ToolModel):
    resource_type: Literal['CloudCompare'] = 'CloudCompare'
