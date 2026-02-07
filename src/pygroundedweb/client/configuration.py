from typing import List

from .base import APIModelClient
from ..models.configuration import Configuration


class ConfigurationClient(APIModelClient):

    def _parse_json(self, config_json: dict) -> Configuration:
        config_json["mutable_fields"] = ["name", "scale_bars", "detector", "cloud_processor", "sfm",
                                         "display_padding"]
        instance = Configuration.model_validate(config_json)
        object.__setattr__(instance, "_client", self)
        return instance

    def create(self, configuration: Configuration) -> Configuration:
        data = configuration.model_dump()
        config_json = self._client.create("configurations", data)
        return self._parse_json(config_json)

    def retrieve(self, config_id: int) -> Configuration:
        config_json = self._client.get_by_id("configurations", config_id)
        return self._parse_json(config_json)

    def update(self, configuration: Configuration) -> Configuration:
        config_json = self._client.update("configurations", configuration)
        return self._parse_json(config_json)

    def delete(self, config_id: int) -> None:
        self._client.delete_by_id("configurations", config_id)

    def list(self) -> List[Configuration]:
        configs_data = self._client.get_all("configurations")
        return [self._parse_json(c) for c in configs_data]