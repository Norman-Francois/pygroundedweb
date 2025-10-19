from __future__ import annotations

from typing import Literal

from ..base import ToolModel


class CCTag(ToolModel):
    resource_type: Literal['CCTag'] = 'CCTag'
