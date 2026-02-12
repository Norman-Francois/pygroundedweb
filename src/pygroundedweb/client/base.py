import logging
import time
from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Any, Dict, List, Optional

import requests

from ..models.base import APIModel
from ..models.user import User
from .exception import APIError, NetworkError, PermissionDenied

logger = logging.getLogger(__name__)

class BaseAPIClient:
    def __init__(self, base_url: str, default_headers: Optional[Dict[str, str]] = None):
        """
        Client HTTP générique qui conserve la session et les cookies.
        :param base_url: URL de base de l'API (ex: "http://localhost:8000/api")
        :param default_headers: headers ajoutés à chaque requête
        """
        self.current_user = None
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.hooks['response'] = [self._log_request]
        self.default_headers = default_headers or {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

    @staticmethod
    def _log_request(response: requests.Response, *args, **kwargs):
        req = response.request
        logger.debug(f"→ {req.method} {req.url}")
        logger.debug(f"  Req headers: {dict(req.headers)}")
        logger.debug(f"  Req body: {req.body}")
        logger.debug(f"← Status: {response.status_code}")
        logger.debug(f"  Resp headers: {dict(response.headers)}")
        logger.debug(f"  Resp body: {response.text}")

    def request(
            self,
            method: str,
            endpoint: str,
            *,
            params: Optional[Dict[str, Any]] = None,
            json: Optional[Any] = None,
            data: Optional[Any] = None,
            headers: Optional[Dict[str, str]] = None,
            allow_refresh: bool = True,
            max_retries: int = 3,
            **kwargs
    ) -> requests.Response:
        url = f"{self.base_url}/{endpoint.rstrip("/")}/"
        hdrs = {**self.default_headers, **(headers or {})}

        for attempt in range(1, max_retries + 1):
            try:
                resp = self.session.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=json,
                    data=data,
                    headers=hdrs,
                    **kwargs
                )
                resp.raise_for_status()
                return resp

            except requests.HTTPError as e:
                status = e.response.status_code if e.response else None
                if status == HTTPStatus.UNAUTHORIZED and allow_refresh:
                    self.refresh()
                    return self.request(
                        method, endpoint,
                        params=params, json=json, data=data,
                        headers=headers, allow_refresh=False,
                        max_retries=max_retries, **kwargs
                    )
                # Unauthorized/Forbidden → permission denied
                if status in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
                    raise PermissionDenied(f"Accès refusé ({status}) sur {url}")
                # 5xx → erreur réseau
                if status and 500 <= status < 600:
                    raise NetworkError(f"Erreur serveur ({status}) sur {url}")
                # autres erreurs API
                phrase = HTTPStatus(status).phrase if status else "Inconnu"
                text = e.response.text if e.response is not None else ""
                raise APIError(f"HTTP {status} ({phrase}) reçu pour {url} : {text}")

            except requests.RequestException as e:
                logger.warning(f"Erreur réseau, tentative {attempt}/{max_retries} : {e}")
                time.sleep(2 ** attempt)

        # Si on n'a toujours pas réussi
        raise NetworkError(f"Échec réseau après {max_retries} tentatives sur {url}")

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request('POST', endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request('PATCH', endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request('PUT', endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request('DELETE', endpoint, **kwargs)

    def _retrieve_current_user(self):
        user_json = self.get('auth/user/').json()
        self.current_user = User.model_validate(user_json)

    def login(self, email: str, password: str):
        try:
            self.post(
                'auth/login/',
                json={'email': email, 'password': password},
                allow_refresh=False
            )
            logger.info("Authentification réussie.")
            logger.debug(f"Cookies reçus : {self.session.cookies.get_dict()}")
            self._retrieve_current_user()
        except APIError as e:
            if "400" in str(e):
                logger.error(f"Échec de l'authentification pour {email} : Identifiants incorrects.")
                raise PermissionDenied("Identifiants incorrects (Email ou mot de passe invalide).") from e

            logger.error(f"Erreur lors de l'authentification de {email} : {e}")
            raise e

    def logout(self):
        try:
            self.post('auth/logout/')
            logger.info("Déconnexion réussie.")
        except (NetworkError, PermissionDenied, APIError, requests.RequestException) as e:
            logger.error(f"Erreur lors de la requête de déconnexion : {e}")
            raise e
        finally:
            self.session.cookies.clear()
            self.current_user = None
            logger.debug("Session locale nettoyée (Cookies supprimés).")

    def refresh(self) -> bool:
        try:
            self.post('auth/token/refresh/',
                      allow_refresh=False)
            return True
        except (NetworkError, PermissionDenied, APIError, requests.RequestException) as e:
            logger.error(f"Échec du rafraîchissement du token : {e}")
            return False

    @property
    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def get_by_id(self, resource: str, id: int) -> Any:
        resp = self.get(f"{resource}/{id}")
        return resp.json()

    def update(self, resource: str, model: APIModel) -> Any:
        resp = self.patch(f"{resource}/{model.pk}/", json=model.model_dump())
        return resp.json()

    def create(self, resource: str, data: Dict[str, Any]) -> Any:
        resp = self.post(f"{resource}", json=data)
        return resp.json()

    def delete_by_id(self, resource: str, id: int):
        response = self.delete(f"{resource}/{id}/")
        return response.json()

    def get_all(self, resource: str, query_string: Dict[str, Any]) -> List[Any]:
        response = self.get(f"/{resource}/", params=query_string)
        return response.json()

    def close(self):
        self.session.close()


class APIModelClient(ABC):
    def __init__(self, client: BaseAPIClient):
        self._client = client

    @abstractmethod
    def create(self, **kwargs) -> APIModel:
        """Crée une nouvelle ressource."""
        pass

    @abstractmethod
    def retrieve(self, resource_id: int) -> APIModel:
        """Récupère une ressource par son ID."""
        pass

    @abstractmethod
    def update(self, instance: APIModel) -> APIModel:
        """Met à jour une instance existante."""
        pass

    @abstractmethod
    def delete(self, resource_id: int) -> None:
        """Supprime une ressource."""
        pass