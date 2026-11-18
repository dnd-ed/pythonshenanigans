"""The :class:`Character` builder and loader.

Unlike libjjs, a :class:`Character` can be *loaded* from an existing character
code with :meth:`Character.from_code`. Loaded entries are kept verbatim, so
fields the library does not model (``TOOL TIP``, awakening ``COLOR``, editor
``PREVIEW`` metadata, unknown nodes, ...) survive a decode -> edit -> encode
round trip untouched.
"""

from __future__ import annotations

import json
from typing import Any, Iterator, Literal

from . import codec
from .defaults import CONDITIONS_DEFAULTS, NODE_DEFAULTS, PROPERTIES_DEFAULTS
from .errors import InvalidCharacterCodeError
from .nodes import VISUAL
from .types import BodyParts, GenericSkill
from .utils import Properties

__all__ = ["Character"]

SkillKind = Literal["SKILL", "SPECIAL", "MELEE", "CHASE", "AWAKENING"]


def _strip_node_defaults(node: dict) -> dict:
    """Drop entries whose value equals the node type's default."""
    k_name = node.get("K_NAME")
    defaults = NODE_DEFAULTS.get(k_name)
    if not defaults:
        return node
    return {
        k: v
        for k, v in node.items()
        if k == "K_NAME" or k not in defaults or defaults[k] != v
    }


def _strip_condition_defaults(condition: dict) -> dict:
    """Drop entries whose value equals the condition type's default."""
    k_name = condition.get("K_NAME")
    defaults = CONDITIONS_DEFAULTS.get(k_name)
    if not defaults:
        return condition
    return {
        k: v
        for k, v in condition.items()
        if k == "K_NAME" or k not in defaults or defaults[k] != v
    }


def _strip_property_defaults(properties: dict) -> dict:
    """Drop properties whose value equals the property default."""
    return {
        k: v
        for k, v in properties.items()
        if not (k in PROPERTIES_DEFAULTS and PROPERTIES_DEFAULTS[k] == v)
    }


class Character:
    """A Jujutsu Shenanigans moveset, built from scratch or loaded from a code."""

    def __init__(
        self,
        hide_character_extras: bool = False,
        raw: list[GenericSkill] | None = None,
    ):
        """Initialise a character.

        :param hide_character_extras: Prepend a hidden skill that hides the
            character's body (this *also* hides player accessories like hair).
            Ignored when ``raw`` is given.
        :param raw: An existing payload to wrap (e.g. the result of
            :func:`pythonshenanigans.codec.decode`). Entries are kept as-is.
        """
        self.raw: list[GenericSkill] = list(raw) if raw is not None else []
        self.create = self.CreateHelper(self)
        if raw is None and hide_character_extras:
            self.create.skill(
                "init__HideCharacterExtras",
                [
                    # hide everything
                    VISUAL("Visibility", opacity=1, alt_opacity=1),
                    # show limbs
                    *[
                        VISUAL("Visibility", opacity=0, alt_opacity=0, limb=limb)
                        for limb in [
                            p for p in BodyParts.__args__ if p != "HumanoidRootPart"
                        ]
                    ],
                ],
                # KEY 0 is reserved for the hidden skill so that user skills keep
                # starting at 1 instead of colliding with it (a libjjs bug).
                key=0,
                properties=Properties(
                    use_when_obtained=True, hide_in_awakening=True, hide_in_base=True
                ),
            )

    # ------------------------------------------------------------------ #
    # loading / exporting
    # ------------------------------------------------------------------ #
    @classmethod
    def from_code(cls, code: str) -> "Character":
        """Load a character from a JJS character code.

        Every field is preserved verbatim, including ones this library does not
        understand.
        """
        payload = codec.decode(code)
        if not isinstance(payload, list):
            raise InvalidCharacterCodeError(
                "top-level payload is not a list of skills"
            )
        return cls(raw=payload)

    @classmethod
    def from_raw(cls, raw_json: str) -> "Character":
        """Load a character from a raw JSON string (the inner that a code holds)."""
        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            raise InvalidCharacterCodeError(
                f"raw payload is not valid JSON: {exc}"
            ) from exc
        if not isinstance(payload, list):
            raise InvalidCharacterCodeError(
                "top-level payload is not a list of skills"
            )
        return cls(raw=payload)

    def create_raw_skill(self, skill_data: GenericSkill) -> None:
        """Append a raw skill dict to the character.

        :param skill_data: The skill to add, already in JJS shape.
        """
        self.raw.append(skill_data)

    def export_raw(self) -> str:
        """Export the character as a raw JSON string."""
        return json.dumps(self.raw, separators=(",", ":"), ensure_ascii=False)

    def export_character_code(self) -> str:
        """Export the character as a JJS-compatible character code."""
        return codec.compress(self.export_raw())

    #: Alias for :meth:`export_character_code`, reads better in a pipeline.
    to_code = export_character_code

    # ------------------------------------------------------------------ #
    # introspection
    # ------------------------------------------------------------------ #
    def __len__(self) -> int:
        return len(self.raw)

    def __iter__(self) -> Iterator[GenericSkill]:
        return iter(self.raw)

    @property
    def skills(self) -> list[dict[str, Any]]:
        """A list of ``{"kind", "name"}`` for every entry, in order."""
        return [
            {"kind": s.get("K_NAME"), "name": s.get("NAME")} for s in self.raw
        ]

    def _used_keys(self) -> set[int]:
        return {
            s["KEY"]
            for s in self.raw
            if s.get("K_NAME") == "SKILL" and isinstance(s.get("KEY"), int)
        }

    def _next_key(self) -> int:
        used = self._used_keys()
        key = 1
        while key in used:
            key += 1
        return key

    # ------------------------------------------------------------------ #
    # building
    # ------------------------------------------------------------------ #
    class CreateHelper:
        def __init__(self, character: "Character"):
            self.character = character

        @staticmethod
        def _build_data(
            line: list[dict],
            properties: dict | None = None,
            conditions: list[dict] | None = None,
            branches: dict[str, dict] | None = None,
        ) -> str:
            # remove default properties
            clean_props = _strip_property_defaults(properties or {})
            # clean default values in nodes
            clean_line = [_strip_node_defaults(node) for node in line]
            # clean conditions
            clean_conds = [
                _strip_condition_defaults(cond) for cond in (conditions or [])
            ]
            # clean branches
            clean_branches: dict[str, dict] = {}
            for branch_name, branch_data in (branches or {}).items():
                clean_branches[branch_name] = {
                    "Line": [
                        _strip_node_defaults(node)
                        for node in branch_data["nodes"]
                    ],
                    "Req": [
                        _strip_condition_defaults(cond)
                        for cond in (branch_data.get("conditions") or [])
                    ],
                }

            data: dict[str, Any] = {
                "Line": clean_line,
                "Prop": clean_props,
                "Req": clean_conds,
            }
            if clean_branches:
                data["Branch"] = clean_branches

            return json.dumps(data, separators=(",", ":"), ensure_ascii=False)

        def skill(
            self,
            name: str,
            line: list[dict] | None = None,
            kind: SkillKind = "SKILL",
            cooldown: float = 0,
            key: int | None = None,
            add: bool = False,
            duration: int | None = None,
            delay: int | None = None,
            properties: dict | None = None,
            conditions: list[dict] | None = None,
            branches: dict[str, dict] | None = None,
            tooltip: str | None = None,
            color: str | None = None,
            extra: dict | None = None,
        ) -> None:
            """Create a skill for the character.

            :param name: The name of the skill.
            :param line: A list of skill nodes. Use ``pythonshenanigans.nodes``.
                May be omitted to create a skill with an empty node graph.
            :param kind: The kind of skill.
            :param cooldown: The cooldown in seconds (``SKILL``/``SPECIAL``/``CHASE``).
            :param key: The key of the skill. Leave ``None`` to auto-assign.
            :param add: Unknown; mirrors the game's ``ADD`` field.
            :param duration: ``AWAKENING`` only --- duration in seconds.
            :param delay: ``AWAKENING`` only --- mirrors the game's ``DELAY`` field.
            :param properties: Use :func:`pythonshenanigans.Properties`.
            :param conditions: Use ``pythonshenanigans.conditions``.
            :param branches: Use :func:`pythonshenanigans.Branch`.
            :param tooltip: Tooltip text shown on the skill (``TOOL TIP``).
            :param color: ``AWAKENING`` only --- a start/end RGB pair such as
                ``"1,1,1 5,5,5"``.
            :param extra: Extra top-level fields to merge in verbatim, escape
                hatch for anything not modelled here.
            """
            if kind not in ("SKILL", "SPECIAL", "MELEE", "CHASE", "AWAKENING"):
                raise ValueError(f"unknown skill kind: {kind!r}")

            data: dict[str, Any] = {
                "NAME": name,
                "DATA": self._build_data(line or [], properties, conditions, branches),
                "K_NAME": kind,
            }
            if kind == "SKILL":
                if cooldown is not None:
                    data["COOLDOWN"] = cooldown
                data["KEY"] = key if key is not None else self.character._next_key()
                if add:
                    data["ADD"] = add
            elif kind in ("SPECIAL", "CHASE"):
                if cooldown is not None:
                    data["COOLDOWN"] = cooldown
            elif kind == "AWAKENING":
                if duration is not None:
                    data["DURATION"] = duration
                if delay is not None:
                    data["DELAY"] = delay
                if color is not None:
                    data["COLOR"] = color
            if tooltip is not None:
                data["TOOL TIP"] = tooltip
            if extra:
                data.update(extra)
            self.character.create_raw_skill(data)
