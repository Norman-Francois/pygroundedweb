"""Classes de base pour les modèles Pydantic utilisés par le client.

Contient la classe `APIModel` qui étend `pydantic.BaseModel` avec :
- gestion des champs mutables/immuables par instance,
- référence vers le client API pour opérations (`refresh`).

Ces docstrings servent à produire une documentation claire des comportements attendus
lors de l'utilisation des objets retournés par l'API.
"""

from abc import ABC
from typing import Set, Optional, TYPE_CHECKING

from pydantic import BaseModel, PrivateAttr, model_validator

if TYPE_CHECKING:
    from ..client.base import APIModelClient


class APIModel(BaseModel, ABC):
    """Base pour les modèles sérialisés provenant de l'API Grounded Web.

    Attributs principaux :
        pk: identifiant numérique si présent.
        _mutable_fields: ensemble des noms de champs modifiables pour cette instance.
        _client: référence (privée) vers le client API permettant d'effectuer des opérations serveur.

    Comportement important :
        - Le constructeur accepte `mutable_fields` ou `immutable_fields` dans les données
          pour contrôler quels attributs peuvent être modifiés localement via setattr.
        - La méthode `refresh()` permet de rafraîchir l'objet à partir du serveur en
          utilisant le client attaché.
    """
    pk: Optional[int] = None
    _mutable_fields: Set[str] = PrivateAttr(default_factory=set)
    _client: Optional['APIModelClient'] = PrivateAttr(default_factory=set)

    def __init__(
            self,
            *,
            mutable_fields: set[str] = None,
            immutable_fields: set[str] = None,
            **data
    ):
        all_fields = set(self.__class__.model_fields.keys())

        if mutable_fields is not None:
            final_mutable = mutable_fields
        elif immutable_fields is not None:
            final_mutable = all_fields - set(immutable_fields)
        else:
            final_mutable = all_fields

        self._validate_fields_exist(final_mutable, label="mutable_fields")
        if immutable_fields is not None:
            self._validate_fields_exist(immutable_fields, label="immutable_fields")

        data.pop('mutable_fields', None)
        data.pop('immutable_fields', None)

        super().__init__(**data)
        object.__setattr__(self, '_mutable_fields', final_mutable)

    @model_validator(mode="after")
    def _set_mutability(self) -> 'APIModel':
        """Validator Pydantic qui met à jour `_mutable_fields` après création.

        Ce validator permet d'accepter des indicateurs `mutable_fields`/`immutable_fields`
        venant directement du JSON serveur.
        """
        data = self.model_extra or {}

        mutable_fields = data.get("mutable_fields")
        immutable_fields = data.get("immutable_fields")

        all_fields = set(self.__class__.model_fields.keys())

        if mutable_fields is not None:
            final_mutable = set(mutable_fields)
        elif immutable_fields is not None:
            final_mutable = all_fields - set(immutable_fields)
        else:
            final_mutable = all_fields

        self._validate_fields_exist(final_mutable, label="mutable_fields")
        if immutable_fields is not None:
            self._validate_fields_exist(set(immutable_fields), label="immutable_fields")

        object.__setattr__(self, "_mutable_fields", final_mutable)
        return self

    def __setattr__(self, name: str, value) -> None:
        """Empêche la modification d'un champ non mutable pour cette instance.

        Lève `AttributeError` si on tente d'affecter un champ présent mais non mutable.
        """
        if hasattr(self, name) and name not in self._mutable_fields:
            raise AttributeError(f"Field '{name}' is immutable for this instance")
        super().__setattr__(name, value)

    def _validate_fields_exist(self, fields: set[str], label: str) -> None:
        """Valide que les champs donnés existent dans le modèle.

        Args:
            fields: ensemble des noms de champs à vérifier.
            label: libellé à utiliser dans les messages d'erreur.
        """
        all_fields = set(self.__class__.model_fields.keys())
        unknown = set(fields) - all_fields
        if unknown:
            raise ValueError(f"Unknown field(s) in {label}: {unknown}")

    def is_mutable(self, field: str) -> bool:
        """Retourne True si le champ donné est modifiable pour cette instance.

        Args:
            field: nom du champ à tester.
        """
        self._validate_fields_exist({field}, label="is_mutable")
        return field in self._mutable_fields

    def refresh(self) -> None:
        """Rafraîchit l'instance actuelle avec les données du serveur.

        Cette méthode utilise le client attaché (`_client`) et l'attribut `pk` pour
        récupérer la version la plus récente du serveur et mettre à jour l'objet local.

        Raises:
            RuntimeError: si le client n'est pas attaché ou si `pk` est None.
        """
        if not self._client or self.pk is None:
            raise RuntimeError("Refresh impossible : client manquant ou pk nulle.")

        fresh_obj = self._client.retrieve(self.pk)

        self.__dict__.update(fresh_obj.__dict__)
        object.__setattr__(self, "_mutable_fields", fresh_obj._mutable_fields)

