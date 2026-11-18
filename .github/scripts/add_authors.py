#!/usr/bin/env python3
"""Check (or add) git contributors in ``[project] authors`` of pyproject.toml.

With ``--check`` this only *reports* contributors who are not listed, and exits
0 either way, so it is safe to run in CI on every push. Without ``--check`` the
missing contributors are appended to pyproject.toml.

Identities are read through ``git log``'s ``%aN``/``%aE``, which respect
``.mailmap`` -- that is how the same person committing under two names/emails is
collapsed into a single entry. Identities listed in ``.github/authors-ignore.txt``
are never credited.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import tomlkit

PYPROJECT = Path("pyproject.toml")
IGNORE_FILE = Path(".github/authors-ignore.txt")

# Identities that must never be credited as an author.
IGNORE_NAME = re.compile(r"\[bot\]|^github actions$|^dependabot$", re.IGNORECASE)
IGNORE_EMAIL = re.compile(
    r"^(action|bot|noreply)@|github-actions\[bot\]@", re.IGNORECASE
)


def load_ignore() -> tuple[set[str], set[str]]:
    """Return ``(names, emails)`` to never credit, from the ignore file.

    Each non-comment line may be an email, a name, or ``Name <email>``.
    """
    if not IGNORE_FILE.exists():
        return set(), set()
    names: set[str] = set()
    emails: set[str] = set()
    for raw in IGNORE_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "<" in line and ">" in line:
            name, _, rest = line.partition("<")
            if name.strip():
                names.add(name.strip().lower())
            address = rest.partition(">")[0].strip()
            if address:
                emails.add(address.lower())
        elif "@" in line:
            emails.add(line.lower())
        else:
            names.add(line.lower())
    return names, emails


def git_authors() -> list[tuple[str, str]]:
    """Return unique ``(name, email)`` pairs from the whole history, in order."""
    ignore_names, ignore_emails = load_ignore()
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
        if name.strip().lower() in ignore_names or email.lower() in ignore_emails:
            continue
        key = email.lower()
        if key in seen:
            continue
        seen.add(key)
        authors.append((name, email))
    return authors


def _existing(authors) -> set[str]:
    """Emails already credited in ``[project] authors``.

    Matching is by email only. Deduping on name as well silently under-credited
    two different contributors who happen to share a name. The one-person /
    several-identities case that name-matching was compensating for is handled
    properly by ``.mailmap``.
    """
    return {
        str(entry.get("email", "")).lower()
        for entry in authors
        if hasattr(entry, "get")
    }


def main(argv: list[str] | None = None) -> int:
    check = "--check" in (argv if argv is not None else sys.argv[1:])

    document = tomlkit.parse(PYPROJECT.read_text(encoding="utf-8"))
    project = document["project"]
    if "authors" not in project:
        project["authors"] = tomlkit.array().multiline(True)
    authors = project["authors"]

    existing_emails = _existing(authors)
    missing = [
        (name, email)
        for name, email in git_authors()
        if email.lower() not in existing_emails
    ]

    if not missing:
        print("all contributors are already listed")
        return 0

    if check:
        # Emitted as GitHub annotations when run in Actions.
        for name, email in missing:
            print(
                f"::warning::contributor not listed in pyproject.toml: "
                f"{name} <{email}>"
            )
        return 0

    for name, email in missing:
        entry = tomlkit.inline_table()
        entry["name"] = name
        entry["email"] = email
        authors.append(entry)
    PYPROJECT.write_text(tomlkit.dumps(document), encoding="utf-8")

    print("added authors:")
    for name, email in missing:
        print(f"  {name} <{email}>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
