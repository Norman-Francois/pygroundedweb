from typing import Optional

from .base import BaseAPIClient
from .configuration import ConfigurationClient
from .dataset import DatasetClient
from .analysis import AnalysisClient
from ..models.user import User


class GroundedWebClient:
    def __init__(self, base_url: str):
        self._api = BaseAPIClient(base_url)
        self.dataset = DatasetClient(self._api)
        self.analysis = AnalysisClient(self._api)
        self.configuration = ConfigurationClient(self._api)

    def login(self, email: str, password: str):
        self._api.login(email, password)

    def logout(self):
        self._api.logout()

    @property
    def is_authenticated(self) -> bool:
        return self._api.is_authenticated

    @property
    def current_user(self) -> Optional[User]:
        return self._api.current_user