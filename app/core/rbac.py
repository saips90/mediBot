from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROLE_COLLECTIONS: dict[str, list[str]] = {
    "doctor": ["clinical", "general"],
    "nurse": ["nursing", "general"],
    "billing_executive": ["billing", "general"],
    "technician": ["equipment", "general"],
    "admin": ["general", "clinical", "nursing", "billing", "equipment"],
}

COLLECTION_ROLES: dict[str, list[str]] = {
    "general": ["doctor", "nurse", "billing_executive", "technician", "admin"],
    "clinical": ["doctor", "admin"],
    "nursing": ["nurse", "admin"],
    "billing": ["billing_executive", "admin"],
    "equipment": ["technician", "admin"],
}

DEMO_USERS: dict[str, dict[str, str]] = {
    "doctor": {"password": "doctor123", "role": "doctor"},
    "nurse": {"password": "nurse123", "role": "nurse"},
    "billing": {"password": "billing123", "role": "billing_executive"},
    "technician": {"password": "tech123", "role": "technician"},
    "admin": {"password": "admin123", "role": "admin"},
}

SQL_RAG_ROLES = {"billing_executive", "admin"}


@dataclass(frozen=True)
class CollectionMetadata:
    collection: str
    access_roles: list[str]


def collection_from_path(path: Path, data_dir: Path) -> CollectionMetadata:
    try:
        relative = path.relative_to(data_dir)
        collection = relative.parts[0]
    except ValueError:
        collection = "general"

    if collection == "db":
        collection = "general"

    access_roles = COLLECTION_ROLES.get(collection, COLLECTION_ROLES["general"])
    return CollectionMetadata(collection=collection, access_roles=access_roles)


def collections_for_role(role: str) -> list[str]:
    return ROLE_COLLECTIONS.get(role, [])


def is_valid_role(role: str) -> bool:
    return role in ROLE_COLLECTIONS
