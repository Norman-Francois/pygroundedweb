from typing import Optional, List

from .base import APIModelClient
from ..models.analysis import Analysis
from ..models.configuration import Configuration
from ..models.dataset import Dataset


class AnalysisClient(APIModelClient):

    def _parse_json(self, analysis_json: str) -> Analysis:
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
        analysis_json = self._client.get_by_id("analyzes", analysis_id)
        analysis_json["mutable_fields"] = ["name", "notify_by_email"]
        return self._parse_json(analysis_json)

    def update(self, analysis: Analysis) -> Analysis:
        analysis_json = self._client.update("analyzes", analysis)
        analysis_json["mutable_fields"] = ["name", "notify_by_email"]
        return self._parse_json(analysis_json)

    def delete(self, analysis_id: int):
        self._client.delete_by_id("analyzes", analysis_id)