from typing import Optional, List

from .base import BaseAPIClient
from ..models.analysis import Analysis
from ..models.dataset import Dataset


class AnalysisClient:
    def __init__(self, client: BaseAPIClient):
        self._client = client

    def create(
            self,
            analysis_name: str,
            notify_by_email: Optional[bool] = False,
            dataset: Optional[Dataset] = None,
            dataset_id: Optional[int] = None,
            selected_photos_id: Optional[List[int]] = None
    ) -> Analysis:

        if not ((dataset is None) ^ (dataset_id is None)):
            raise ValueError("You must provide either 'dataset' or 'dataset_id', but not both.")

        if dataset is not None:
            dataset_id = dataset.pk

        data_analysis = {
            "name": analysis_name,
            "notify_by_email": notify_by_email,
            "selection": {
                "dataset_id": dataset_id,
                "photos_ids": selected_photos_id
            }
        }

        analysis_json = self._client.create("analyzes", data_analysis)
        analysis_json["mutable_fields"] = ["name", "notify_by_email"]
        return Analysis.model_validate(analysis_json)

    def retrieve(self, analysis_id: int):
        analysis_json = self._client.get_by_id("analyzes", analysis_id)
        analysis_json["mutable_fields"] = ["name", "notify_by_email"]
        return Analysis.model_validate(analysis_json)

    def update(self, analysis: Analysis):
        analysis_json = self._client.update("analyzes", analysis)
        return Analysis.model_validate(analysis_json)

    def delete(self, analysis_id: int):
        self._client.delete_by_id("analyzes", analysis_id)


