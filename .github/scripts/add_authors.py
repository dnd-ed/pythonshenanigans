#!/usr/bin/env python3
"""Add every git contributor to ``[project] authors`` in pyproject.toml.

Idempotent: contributors already listed are left alone, so running this on every
push is safe. Uses tomlkit so the rest of pyproject.toml is left byte-identical.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import tomlkit

PYPROJECT = Path("pyproject.toml")

# Identities that must never be credited as an author.
IGNORE_NAME = re.compile(r"\[bot\]|^github actions$|^dependabot$", re.IGNORECASE)
IGNORE_EMAIL = re.compile(r"^(action|bot|noreply)@|github-actions\[bot\]@", re.IGNORECASE)


def git_authors() -> list[tuple[str, str]]:
    """Return unique ``(name, email)`` pairs from the whole history, in order."""
    result = subprocess.run(
        ["git", "log", "--format=%aN\t%aE"],
        check=True,
        capture_output=True,
        text=True,
    )
    authors: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        name, email = (part.strip() for part in line.split("\t", 1))
        if not name or not email or "@" not in email:
            continue
        if IGNORE_NAME.search(name) or IGNORE_EMAIL.search(email):
            continue
        key = email.lower()
        if key in seen:
            continue
        seen.add(key)
        authors.append((name, email))
    return authors


def main() -> int:
    document = tomlkit.parse(PYPROJECT.read_text(encoding="utf-8"))
    project = document["project"]

    if "authors" not in project:
        project["authors"] = tomlkit.array().multiline(True)
    authors = project["authors"]

    existing_emails = {
        str(entry.get("email", "")).lower()
        for entry in authors
        if hasattr(entry, "get")
    }
    # Dedupe on name as well: the same person committing from a second address
    # should not be credited twice.
    existing_names = {
        str(entry.get("name", "")).strip().lower()
        for entry in authors
        if hasattr(entry, "get")
    }

    added: list[str] = []
    for name, email in git_authors():
        if email.lower() in existing_emails or name.strip().lower() in existing_names:
            continue
        entry = tomlkit.inline_table()
        entry["name"] = name
        entry["email"] = email
        authors.append(entry)
        existing_emails.add(email.lower())
        existing_names.add(name.strip().lower())
        added.append(f"{name} <{email}>")

    if not added:
        print("no new authors")
        return 0

    PYPROJECT.write_text(tomlkit.dumps(document), encoding="utf-8")
    print("added authors:")
    for author in added:
        print(f"  {author}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
