
from .base import BaseAPIClient
from .dataset import DatasetClient


class GroundedWebClient:
    def __init__(self, base_url: str):
        self._api = BaseAPIClient(base_url)
        self.dataset = DatasetClient(self._api)

    def login(self, email: str, password: str):
        return self._api.login(email, password)

    def logout(self):
        return self._api.logout()

