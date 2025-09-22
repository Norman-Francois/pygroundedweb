from abc import ABC
from typing import Set, Optional

from pydantic import BaseModel, PrivateAttr, model_validator


class APIModel(BaseModel, ABC):
    pk: Optional[int] = None
    _mutable_fields: Set[str] = PrivateAttr(default_factory=set)
    _client: str = PrivateAttr(default_factory=str)

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
            final_mutable = all_fields  # ✅ par défaut : tout est mutable

        # ✅ Validation via méthode privée
        self._validate_fields_exist(final_mutable, label="mutable_fields")
        if immutable_fields is not None:
            self._validate_fields_exist(immutable_fields, label="immutable_fields")

        # Nettoyage
        data.pop('mutable_fields', None)
        data.pop('immutable_fields', None)

        super().__init__(**data)
        object.__setattr__(self, '_mutable_fields', final_mutable)

    @model_validator(mode="after")
    def _set_mutability(self) -> 'APIModel':
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
        if hasattr(self, name) and name not in self._mutable_fields:
            raise AttributeError(f"Field '{name}' is immutable for this instance")
        super().__setattr__(name, value)

    def _validate_fields_exist(self, fields: set[str], label: str) -> None:
        """Valide que les champs donnés existent dans le modèle."""
        all_fields = set(self.__class__.model_fields.keys())
        unknown = set(fields) - all_fields
        if unknown:
            raise ValueError(f"Unknown field(s) in {label}: {unknown}")

    def is_mutable(self, field: str) -> bool:
        self._validate_fields_exist({field}, label="is_mutable")
        return field in self._mutable_fields
