"""Modèle représentant un utilisateur retourné par l'API."""

from __future__ import annotations

from .base import APIModel


class User(APIModel):
    """Représentation minimale d'un utilisateur.

    Champs:
        first_name: prénom.
        last_name: nom.
        email: adresse email.
    """
    first_name: str
    last_name: str
    email: str