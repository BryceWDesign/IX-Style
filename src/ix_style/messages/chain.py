"""Tamper-evident hash-chaining utilities for IX-Style evidence artifacts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

GENESIS_MARKER = "IX-STYLE-EVIDENCE-GENESIS"


def canonicalize_document(document: dict[str, Any]) -> bytes:
    """Return a canonical byte representation of a document."""
    return json.dumps(
        _normalize(document),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def hash_document(document: dict[str, Any]) -> str:
    """Return a SHA-256 hash for a canonical document."""
    return hashlib.sha256(canonicalize_document(document)).hexdigest()


def hash_chain_step(
    *,
    item_index: int,
    item_type: str,
    item_id: str,
    previous_chain_hash: str,
    item_hash: str,
) -> str:
    """Return the deterministic chain hash for one item."""
    if item_index < 0:
        raise ValueError("item_index must be non-negative")
    if not item_type.strip():
        raise ValueError("item_type must not be empty")
    if not item_id.strip():
        raise ValueError("item_id must not be empty")
    if not previous_chain_hash.strip():
        raise ValueError("previous_chain_hash must not be empty")
    if not item_hash.strip():
        raise ValueError("item_hash must not be empty")

    joined = "|".join(
        [
            str(item_index),
            item_type,
            item_id,
            previous_chain_hash,
            item_hash,
        ]
    ).encode("utf-8")
    return hashlib.sha256(joined).hexdigest()


@dataclass(slots=True, frozen=True)
class ChainLink:
    """One deterministic chain link over a bundle item."""

    item_index: int
    item_type: str
    item_id: str
    item_hash: str
    previous_chain_hash: str
    chain_hash: str


class EvidenceChain:
    """Build and verify deterministic IX-Style evidence chains."""

    def build_links(
        self,
        items: list[tuple[str, str, dict[str, Any]]],
    ) -> tuple[tuple[ChainLink, ...], str]:
        """Build chain links for ordered bundle items and return the head hash."""
        links: list[ChainLink] = []
        previous = GENESIS_MARKER

        for index, (item_type, item_id, document) in enumerate(items):
            item_hash = hash_document(document)
            chain_hash = hash_chain_step(
                item_index=index,
                item_type=item_type,
                item_id=item_id,
                previous_chain_hash=previous,
                item_hash=item_hash,
            )
            links.append(
                ChainLink(
                    item_index=index,
                    item_type=item_type,
                    item_id=item_id,
                    item_hash=item_hash,
                    previous_chain_hash=previous,
                    chain_hash=chain_hash,
                )
            )
            previous = chain_hash

        return tuple(links), previous

    def verify_links(
        self,
        items: list[tuple[str, str, dict[str, Any]]],
        links: list[dict[str, Any]] | tuple[dict[str, Any], ...],
        *,
        expected_head_chain_hash: str,
    ) -> tuple[str, ...]:
        """Return validation errors for a supplied chain."""
        errors: list[str] = []

        if len(items) != len(links):
            errors.append(
                "item count does not match chain link count"
            )
            return tuple(errors)

        previous = GENESIS_MARKER
        expected_head = previous

        for index, ((item_type, item_id, document), link) in enumerate(zip(items, links)):
            expected_item_hash = hash_document(document)
            expected_chain_hash = hash_chain_step(
                item_index=index,
                item_type=item_type,
                item_id=item_id,
                previous_chain_hash=previous,
                item_hash=expected_item_hash,
            )

            if link.get("item_index") != index:
                errors.append(f"link[{index}].item_index mismatch")
            if link.get("item_type") != item_type:
                errors.append(f"link[{index}].item_type mismatch")
            if link.get("item_id") != item_id:
                errors.append(f"link[{index}].item_id mismatch")
            if link.get("item_hash") != expected_item_hash:
                errors.append(f"link[{index}].item_hash mismatch")
            if link.get("previous_chain_hash") != previous:
                errors.append(f"link[{index}].previous_chain_hash mismatch")
            if link.get("chain_hash") != expected_chain_hash:
                errors.append(f"link[{index}].chain_hash mismatch")

            previous = expected_chain_hash
            expected_head = expected_chain_hash

        if expected_head_chain_hash != expected_head:
            errors.append("bundle head_chain_hash mismatch")

        return tuple(errors)


def _normalize(value: Any) -> Any:
    """Convert values into deterministic JSON-friendly primitives."""
    if isinstance(value, dict):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize(item) for item in value]
    if isinstance(value, set):
        return sorted(_normalize(item) for item in value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    return value
