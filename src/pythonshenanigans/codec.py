"""The character-code codec.

A Jujutsu Shenanigans character code is::

    base64( zstd( json ) )

where the JSON is the (minified) ``list`` of skill objects. Nothing else is
layered on top --- the zstd frame is a plain standard frame and the base64 uses
the standard alphabet, so decoding is fully reversible.

This module is deliberately backend-agnostic. A zstd implementation is chosen
automatically, in this order:

1. ``compression.zstd`` (Python 3.14+ standard library)
2. ``zstd``
3. ``pyzstd``
4. ``zstandard``

Set the ``PYTHONSHENANIGANS_ZSTD_BACKEND`` environment variable (e.g. to
``"pyzstd"``) to prefer a specific one; the rest stay as fallbacks.

Every supported backend emits a **single-segment** frame, which declares the
content size --- the same header shape the game's own codes use, so generated
codes round-trip identically. The test suite asserts that against a real
game-produced code, for whichever backend is active; CI covers the standard
library, ``pyzstd`` and ``zstandard``.

Note: libjjs depended on the ``zstd`` package, but its newest release is yanked
on PyPI, so it survives here only as an opportunistic fallback.
"""

from __future__ import annotations

import base64
import binascii
import io
import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .errors import BackendNotFoundError, InvalidCharacterCodeError

__all__ = [
    "ENV_BACKEND",
    "ZSTD_MAGIC",
    "backend_name",
    "compress",
    "decode",
    "decompress",
    "encode",
]

#: Every zstd frame begins with these four bytes.
ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"

#: Environment variable used to prefer a specific zstd backend.
ENV_BACKEND = "PYTHONSHENANIGANS_ZSTD_BACKEND"

#: The first four base64 characters of any character code (``ZSTD_MAGIC``).
_MAGIC_B64_PREFIX = "KLUv"


@dataclass(frozen=True)
class _Backend:
    name: str
    compress: Callable[[bytes], bytes]
    decompress: Callable[[bytes], bytes]


def _backend_stdlib() -> _Backend:
    from compression import zstd as _z

    return _Backend("compression.zstd", _z.compress, _z.decompress)


def _backend_zstd() -> _Backend:
    import zstd as _z

    return _Backend("zstd", _z.compress, _z.decompress)


def _backend_pyzstd() -> _Backend:
    import pyzstd as _z

    return _Backend("pyzstd", _z.compress, _z.decompress)


def _backend_zstandard() -> _Backend:
    import zstandard as _z

    def decompress(data: bytes) -> bytes:
        # ``ZstdDecompressor.decompress`` requires the frame's content size,
        # which is not guaranteed, so stream through a reader instead.
        with _z.ZstdDecompressor().stream_reader(io.BytesIO(data)) as reader:
            return reader.read()

    return _Backend("zstandard", _z.ZstdCompressor().compress, decompress)


_BACKENDS: tuple[tuple[str, Callable[[], _Backend]], ...] = (
    ("compression.zstd", _backend_stdlib),
    ("zstd", _backend_zstd),
    ("pyzstd", _backend_pyzstd),
    ("zstandard", _backend_zstandard),
)

_BACKEND: _Backend | None = None


def _load_backend() -> _Backend:
    candidates = list(_BACKENDS)
    preferred = os.environ.get(ENV_BACKEND, "").strip().lower()
    if preferred:
        # Move the requested backend to the front; it still has to import.
        candidates.sort(key=lambda item: item[0] != preferred)

    problems: list[str] = []
    for name, loader in candidates:
        try:
            return loader()
        except Exception as exc:  # ImportError, missing attribute, ...
            problems.append(f"{name}: {type(exc).__name__}: {exc}")

    raise BackendNotFoundError(
        "no usable zstd backend found (tried "
        + ", ".join(problems)
        + "); install 'pyzstd' or 'zstandard', or use Python 3.14+"
    )


def _backend() -> _Backend:
    global _BACKEND
    if _BACKEND is None:
        _BACKEND = _load_backend()
    return _BACKEND


def backend_name() -> str:
    """Return the name of the zstd implementation currently in use."""
    return _backend().name


def _clean_code(code: str) -> str:
    if not isinstance(code, str):
        raise InvalidCharacterCodeError(
            f"expected a string character code, got {type(code).__name__}"
        )
    cleaned = "".join(code.split())
    # Tolerate codes copied with a prefix in front of them (e.g. a "Code: "
    # label) by resyncing on the magic.
    index = cleaned.find(_MAGIC_B64_PREFIX)
    if index > 0:
        cleaned = cleaned[index:]
    return cleaned


def _decode_bytes(code: str) -> bytes:
    cleaned = _clean_code(code)
    if not cleaned:
        raise InvalidCharacterCodeError("empty character code")
    padded = cleaned + "=" * (-len(cleaned) % 4)
    try:
        raw = base64.b64decode(padded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise InvalidCharacterCodeError(f"not valid base64: {exc}") from exc
    if not raw.startswith(ZSTD_MAGIC):
        raise InvalidCharacterCodeError(
            "decoded payload is not a zstd frame; this does not look like a "
            "character code"
        )
    try:
        decompressed = _backend().decompress(raw)
    except Exception as exc:
        raise InvalidCharacterCodeError(f"zstd decompression failed: {exc}") from exc
    if not decompressed:
        # zstandard's stream reader yields b"" for some corrupt frames rather
        # than raising, which would otherwise surface as a misleading JSON error.
        raise InvalidCharacterCodeError(
            "zstd decompression produced no data; the code is corrupt"
        )
    return decompressed


def compress(raw_json: str) -> str:
    """zstd-compress a JSON string and base64-encode the result."""
    return base64.b64encode(
        _backend().compress(raw_json.encode("utf-8"))
    ).decode("ascii")


def decompress(code: str) -> str:
    """Base64-decode ``code`` and zstd-decompress it back into a JSON string."""
    return _decode_bytes(code).decode("utf-8")


def encode(payload: Any) -> str:
    """Serialise a character payload (a list of skills) into a character code."""
    return compress(json.dumps(payload, separators=(",", ":"), ensure_ascii=False))


def decode(code: str) -> Any:
    """Decode a character code back into Python objects."""
    try:
        return json.loads(decompress(code))
    except json.JSONDecodeError as exc:
        raise InvalidCharacterCodeError(
            f"payload is not valid JSON: {exc}"
        ) from exc