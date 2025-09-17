import logging
import time
from http import HTTPStatus
from typing import Any, Dict, List, Optional

import requests

from ..models.base import APIModel
from .exception import APIError, NetworkError, PermissionDenied


class BaseAPIClient:
    def __init__(self, base_url: str, default_headers: Optional[Dict[str, str]] = None):
        """
        Client HTTP générique qui conserve la session et les cookies.
        :param base_url: URL de base de l'API (ex: "http://localhost:8000/api")
        :param default_headers: headers ajoutés à chaque requête
        """
        self.currentUser = None
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
        logging.debug(f"→ {req.method} {req.url}")
        logging.debug(f"  Req headers: {dict(req.headers)}")
        logging.debug(f"  Req body: {req.body}")
        logging.debug(f"← Status: {response.status_code}")
        logging.debug(f"  Resp headers: {dict(response.headers)}")
        logging.debug(f"  Resp body: {response.text}")

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
        url = f"{self.base_url}{endpoint}"
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
                logging.warning(f"Erreur réseau, tentative {attempt}/{max_retries} : {e}")
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

    def login(self, email: str, password: str) -> bool:
        try:
            self.post(
                '/auth/login/',
                json={'email': email, 'password': password},
                allow_refresh=False
            )
            logging.info("Authentification réussie.")
            logging.debug(f"Cookies reçus : {self.session.cookies.get_dict()}")
            return True
        except (NetworkError, PermissionDenied, APIError, requests.RequestException) as e:
            logging.error(f"Échec de l'authentification : {e}")
            return False

    def logout(self) -> bool:
        try:
            self.post('/auth/logout/')
            logging.info("Déconnexion réussie.")
            return True
        except (NetworkError, PermissionDenied, APIError, requests.RequestException) as e:
            logging.error(f"Échec de la déconnexion : {e}")
            return False

    def refresh(self) -> bool:
        try:
            self.post('/auth/token/refresh/')
            return True
        except (NetworkError, PermissionDenied, APIError, requests.RequestException) as e:
            logging.error(f"Échec du rafraîchissement du token : {e}")
            return False

    @property
    def is_connected(self) -> bool:
        return self.currentUser is not None

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
