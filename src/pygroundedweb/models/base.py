from abc import ABC, abstractmethod
from typing import Set

from pydantic import BaseModel, PrivateAttr, model_validator


class APIModel(BaseModel, ABC):
    pk: int

    _mutable_fields: Set[str] = PrivateAttr(default_factory=set)
    _client: str = PrivateAttr(default_factory=str)

    @classmethod
    @model_validator(mode="before")
    def collect_mutability(cls, values: dict) -> dict:
        m = set(values.pop('mutable_fields', []))
        i = set(values.pop('immutable_fields', []))
        if i and not m:
            m = set(cls.model_fields.keys()) - i
        values['_init_mutable_fields'] = m
        return values

    def __init__(self, **data):
        init_m = data.pop('mutable_fields', set())
        super().__init__(**data)
        object.__setattr__(self, '_mutable_fields', init_m)

    def __setattr__(self, name: str, value) -> None:
        if hasattr(self, name) and name not in self._mutable_fields:
            raise AttributeError(f"Field '{name}' is immutable for this instance")
        super().__setattr__(name, value)

    @abstractmethod
    def refresh(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass
