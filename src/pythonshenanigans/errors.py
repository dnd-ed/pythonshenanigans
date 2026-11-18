"""Exceptions raised by :mod:`pythonshenanigans`.

Everything the library raises derives from :class:`PythonshenanigansError`, so
callers can wrap an entire character-code pipeline in a single ``except``.
"""

from __future__ import annotations

__all__ = [
    "BackendNotFoundError",
    "InvalidCharacterCodeError",
    "PythonshenanigansError",
]


class PythonshenanigansError(Exception):
    """Base class for every error raised by this library."""


class InvalidCharacterCodeError(PythonshenanigansError, ValueError):
    """Raised when a string is not a valid Jujutsu Shenanigans character code."""


class BackendNotFoundError(PythonshenanigansError, ImportError):
    """Raised when no usable zstd implementation could be imported."""
