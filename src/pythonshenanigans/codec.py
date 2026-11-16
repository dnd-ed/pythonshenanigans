"""The character-code codec.

A Jujutsu Shenanigans character code is::

    base64( zstd( json ) )

where the JSON is the (minified) ``list`` of skill objects. Nothing else is
layered on top --- the zstd frame is a plain standard frame and the base64 uses
the standard alphabet, so decoding is fully reversible.

This module is deliberately backend-agnostic: it uses whichever zstd
implementation it can find, in this order:

1. ``compression.zstd`` (Python 3.14+ standard library)
2. ``zstd``            (the dependency used by libjjs)
3. ``pyzstd``
4. ``zstandard``

so the library works on 3.13 and 3.14 without pinning a specific binding.
"""

from __future__ import annotations

import base64
import binascii
import json
from dataclasses import dataclass
from typing import Any, Callable

from .errors import BackendNotFoundError, InvalidCharacterCodeError

__all__ = [
    "ZSTD_MAGIC",
    "backend_name",
    "compress",
    "decompress",
    "encode",
    "decode",
]

#: Every zstd frame begins with these four bytes.
ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"

#: The first four base64 characters of any character code (``ZSTD_MAGIC``).
_MAGIC_B64_PREFIX = "KLUv"


@dataclass(frozen=True)
class _Backend:
    name: str
    compress: Callable[[bytes], bytes]
    decompress: Callable[[bytes], bytes]


def _zstandard_decompress(data: bytes) -> bytes:
    # ``ZstdDecompressor.decompress`` needs the frame's content size, which is
    # not guaranteed, so stream through a reader instead.
    import io

    import zstandard

    with zstandard.ZstdDecompressor().stream_reader(io.BytesIO(data)) as reader:
        return reader.read()


def _load_backend() -> _Backend:
    try:  # Python 3.14+ ships zstd in the standard library
        from compression import zstd as _z

        return _Backend("compression.zstd", _z.compress, _z.decompress)
    except Exception:  # pragma: no cover - depends on interpreter version
        pass
    try:
        import zstd as _z

        return _Backend("zstd", _z.compress, _z.decompress)
    except Exception:  # pragma: no cover
        pass
    try:
        import pyzstd as _z

        return _Backend("pyzstd", _z.compress, _z.decompress)
    except Exception:  # pragma: no cover
        pass
    try:
        import zstandard as _z

        return _Backend(
            "zstandard",
            _z.ZstdCompressor().compress,
            _zstandard_decompress,
        )
    except Exception:  # pragma: no cover
        pass
    raise BackendNotFoundError(
        "no zstd backend available; install one of 'zstd', 'pyzstd' or "
        "'zstandard' (Python 3.14+ already ships one in the standard library)"
    )


_BACKEND: _Backend | None = None


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
    # Tolerate codes that were copied with a prefix in front of them (e.g. a
    # ``jjs://`` scheme or an "Code: " label) by resyncing on the magic.
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
        return _backend().decompress(raw)
    except Exception as exc:
        raise InvalidCharacterCodeError(f"zstd decompression failed: {exc}") from exc


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
