"""Client HTTP de base et clients de modèles pour l'API Grounded Web.

Ce module expose :
- BaseAPIClient : client HTTP basique qui gère la session et les appels REST.
- APIModelClient : base abstraite pour les clients de ressources (create/retrieve/update/delete).

Les docstrings détaillent les paramètres et le comportement attendu pour faciliter la génération de documentation.
"""

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
    """Client HTTP générique qui conserve une session persistante et fournit des utilitaires
    pour effectuer des requêtes vers l'API Grounded Web.

    Ce client gère :
    - la construction des URLs (ajoute "/api" si nécessaire),
    - la ré-essai automatique sur erreurs réseau,
    - le rafraîchissement de tokens lorsque nécessaire,
    - la sérialisation/désérialisation minimale des réponses JSON.

    Params
    ------
    base_url: str
        URL de base de l'API (ex: "http://localhost:8000" ou "http://localhost:8000/api").
    default_headers: Optional[Dict[str, str]]
        Headers par défaut pour chaque requête (Accept/Content-Type par défaut si None).
    check_connection: bool
        Si True, effectue une validation initiale de l'API en interrogeant l'endpoint /schema.
    """

    def __init__(self, base_url: str, default_headers: Optional[Dict[str, str]] = None,
                 check_connection: bool = True):
        """Initialise la session et les paramètres du client.

        Note: la validation de l'API peut lever une APIError si l'API distante n'est pas celle attendue.
        """
        self.current_user = None
        self.session = requests.Session()
        self.session.hooks['response'] = [self._log_request]
        self.default_headers = default_headers or {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        clean_url = base_url.strip().rstrip('/')
        if not clean_url.endswith('/api'):
            clean_url += '/api'
        self.base_url = clean_url

        if check_connection:
            self._validate_api()

    @staticmethod
    def _log_request(response: requests.Response, *args, **kwargs):
        """Hook de logging pour chaque réponse HTTP (utilisé par la session requests).

        Ce hook n'affecte pas le flot d'exécution, il sert uniquement à des fins de debug.
        """
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
            endpoint: str = "",
            *,
            params: Optional[Dict[str, Any]] = None,
            json: Optional[Any] = None,
            data: Optional[Any] = None,
            headers: Optional[Dict[str, str]] = None,
            allow_refresh: bool = True,
            max_retries: int = 3,
            full_url: Optional[str] = None,
            **kwargs
    ) -> requests.Response:
        """Effectue une requête HTTP vers l'API en gérant les erreurs communes.

        Args:
            method: Méthode HTTP (GET, POST, PATCH, ...).
            endpoint: Chemin relatif de la ressource (ex: 'datasets').
            params: Paramètres de requête (querystring).
            json: Payload JSON si applicable.
            data: Payload non-JSON si nécessaire.
            headers: En-têtes supplémentaires pour cette requête.
            allow_refresh: Si True, tentera un rafraîchissement du token sur 401.
            max_retries: Nombre maximal de tentatives en cas d'erreur réseau.
            full_url: Utiliser une URL absolue plutôt que base_url/endpoint.

        Returns:
            requests.Response: objet Response déjà vérifié et sans status HTTP erreur.

        Raises:
            APIError, NetworkError, PermissionDenied
        """
        if full_url:
            url = full_url
        else:
            url = f"{self.base_url}/{endpoint.rstrip('/')}/"
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
            except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema,
                    requests.exceptions.InvalidURL) as e:
                raise APIError(f"URL invalide ou protocole manquant : {e}") from e

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
        """Raccourci pour effectuer une requête GET."""
        return self.request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """Raccourci pour effectuer une requête POST."""
        return self.request('POST', endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        """Raccourci pour effectuer une requête PATCH."""
        return self.request('PATCH', endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """Raccourci pour effectuer une requête PUT."""
        return self.request('PUT', endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Raccourci pour effectuer une requête DELETE."""
        return self.request('DELETE', endpoint, **kwargs)

    def _retrieve_current_user(self):
        """Récupère l'utilisateur courant depuis l'API et le stocke dans `current_user`."""
        user_json = self.get('auth/user/').json()
        self.current_user = User.model_validate(user_json)

    def login(self, email: str, password: str):
        """Effectue l'authentification auprès de l'API.

        Args:
            email: adresse email de l'utilisateur.
            password: mot de passe en clair.

        Raises:
            PermissionDenied: si les identifiants sont invalides.
            APIError: pour d'autres erreurs retournées par l'API.
        """
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
        """Se déconnecte de l'API et nettoie la session locale (cookies)."""
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
        """Tente de rafraîchir le token d'authentification via l'endpoint standard.

        Retourne True si le rafraîchissement a réussi, False sinon.
        """
        try:
            self.post('auth/token/refresh/',
                      allow_refresh=False)
            return True
        except (NetworkError, PermissionDenied, APIError, requests.RequestException) as e:
            logger.error(f"Échec du rafraîchissement du token : {e}")
            return False

    @property
    def is_authenticated(self) -> bool:
        """Indique si une session est actuellement authentifiée (user chargé)."""
        return self.current_user is not None

    def get_by_id(self, resource: str, id: int) -> Any:
        """Récupère un objet JSON par ID pour la ressource donnée.

        Args:
            resource: nom de la ressource (ex: 'datasets').
            id: identifiant numérique.

        Returns:
            Le JSON (dictionnaire) retourné par l'API.
        """
        resp = self.get(f"{resource}/{id}")
        return resp.json()

    def update(self, resource: str, model: APIModel) -> Any:
        """Met à jour une ressource en envoyant un PATCH avec le model.serialized.

        Args:
            resource: nom de la ressource.
            model: instance héritant de APIModel.

        Returns:
            Le JSON résultant de la mise à jour.
        """
        resp = self.patch(f"{resource}/{model.pk}/", json=model.model_dump(mode='json'))
        return resp.json()

    def create(self, resource: str, data: Dict[str, Any]) -> Any:
        """Crée une ressource en POSTant les données JSON fournies.

        Args:
            resource: nom de la ressource (ex: 'datasets').
            data: dict contenant les champs à créer.

        Returns:
            Le JSON de la ressource créée (typiquement contient l'ID).
        """
        resp = self.post(f"{resource}", json=data)
        return resp.json()

    def delete_by_id(self, resource: str, id: int):
        """Supprime une ressource par ID et retourne la réponse JSON.

        Args:
            resource: nom de la ressource.
            id: identifiant de la ressource.
        """
        response = self.delete(f"{resource}/{id}/")
        return response.json()

    def get_all(self, resource: str, query_string: Dict[str, Any]) -> List[Any]:
        """Récupère la liste d'objets pour une ressource en utilisant query string.

        Args:
            resource: nom de la ressource.
            query_string: dictionnaire de paramètres de filtrage/pagination.

        Returns:
            Liste d'objets JSON.
        """
        response = self.get(f"/{resource}/", params=query_string)
        return response.json()

    def _validate_api(self):
        """Vérifie que l'API distante est bien une instance attendue en lisant /schema.

        Cette méthode lève APIError si l'API ne répond pas ou si le champ "info.title"
        ne correspond pas à "Grounded Web API".
        """
        schema_url = self.base_url.replace('/api', '/schema')

        try:
            logger.debug(f"Vérification de l'identité API sur {schema_url}...")

            response = self.request(
                method='GET',
                full_url=schema_url,
                allow_refresh=False,
                max_retries=1
            )

            data = response.json()
            api_title = data.get('info', {}).get('title')
            expected_title = "Grounded Web API"

            if api_title != expected_title:
                raise APIError(f"API incorrecte détectée : '{api_title}' (Attendu : {expected_title})")

            logger.info(f"Connexion validée avec {api_title}.")

        except (APIError, NetworkError, PermissionDenied, ValueError) as e:
            raise APIError(f"Impossible de valider l'identité de l'API ({schema_url}) : {e}") from e

    def close(self):
        """Ferme la session HTTP (libère les connexions)."""
        self.session.close()


class APIModelClient(ABC):
    """Base abstraite pour les clients de ressources CRUD.

    Les implémentations doivent exposer les méthodes create/retrieve/update/delete.
    """
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

