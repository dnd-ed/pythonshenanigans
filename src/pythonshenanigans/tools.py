"""Read-only helpers for looking inside a character code you did not build.

These exist because the fastest way to learn what the live game supports is to
decode a code *it* produced and read the fields straight off it.
"""

from __future__ import annotations

import json
from typing import Any

from . import codec
from .errors import InvalidCharacterCodeError

__all__ = ["describe", "dumps"]


def _expand(obj: Any) -> Any:
    """Recursively parse nested ``DATA`` JSON strings into objects."""
    if isinstance(obj, list):
        return [_expand(item) for item in obj]
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for key, value in obj.items():
            if key == "DATA" and isinstance(value, str):
                try:
                    out[key] = _expand(json.loads(value))
                except json.JSONDecodeError:
                    out[key] = value
            else:
                out[key] = _expand(value)
        return out
    return obj


def dumps(code: str, *, indent: int = 2, expand_data: bool = True) -> str:
    """Return the full payload of ``code`` as pretty-printed JSON.

    :param indent: JSON indentation.
    :param expand_data: Parse the nested ``DATA`` strings so the whole node
        graph is visible instead of one escaped blob.
    """
    obj = codec.decode(code)
    if expand_data:
        obj = _expand(obj)
    return json.dumps(obj, indent=indent, ensure_ascii=False)


def describe(code: str) -> dict[str, Any]:
    """Return a compact structural summary of a character code."""
    obj = codec.decode(code)
    if not isinstance(obj, list):
        raise InvalidCharacterCodeError(
            "top-level payload is not a list of skills"
        )

    skills: list[dict[str, Any]] = []
    for entry in obj:
        if not isinstance(entry, dict):
            skills.append({"kind": None, "name": None, "raw": entry})
            continue
        info: dict[str, Any] = {
            "kind": entry.get("K_NAME"),
            "name": entry.get("NAME"),
            "fields": sorted(entry),
        }
        data = entry.get("DATA")
        if isinstance(data, str):
            try:
                inner = json.loads(data)
            except json.JSONDecodeError:
                inner = None
            if isinstance(inner, dict):
                info["nodes"] = [
                    node.get("K_NAME")
                    for node in inner.get("Line", [])
                    if isinstance(node, dict)
                ]
                info["conditions"] = [
                    cond.get("K_NAME")
                    for cond in inner.get("Req", [])
                    if isinstance(cond, dict)
                ]
                branches = inner.get("Branch")
                if branches:
                    info["branches"] = sorted(branches)
        skills.append(info)

    return {"skill_count": len(obj), "skills": skills}
