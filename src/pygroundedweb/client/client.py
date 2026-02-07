from .base import BaseAPIClient
from .configuration import ConfigurationClient
from .dataset import DatasetClient
from .analysis import AnalysisClient


class GroundedWebClient:
    def __init__(self, base_url: str):
        self._api = BaseAPIClient(base_url)
        self.dataset = DatasetClient(self._api)
        self.analysis = AnalysisClient(self._api)
        self.configuration = ConfigurationClient(self._api)

    def login(self, email: str, password: str):
        return self._api.login(email, password)

    def logout(self):
        return self._api.logout()
