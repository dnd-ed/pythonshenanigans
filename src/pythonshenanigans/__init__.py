"""PythonShenanigans --- build, load and modify Jujutsu Shenanigans movesets.

A maintained, extended take on ``libjjs``. On top of everything libjjs could do
it can also:

* **load** an existing character code and edit it (everything is preserved);
* model the ``PARTICLE``, ``LOOK`` and ``SETMELEE`` nodes;
* set the ``TOOL TIP`` (skills) and ``COLOR`` (awakenings) fields;
* round-trip codes without dropping fields it does not understand.

Quick start::

    import pythonshenanigans as pts
    import pythonshenanigans.nodes as nodes

    character = pts.Character()
    character.create.skill("Punch", [nodes.HITBOX(damage=5)])
    code = character.export_character_code()

    loaded = pts.Character.from_code(code)
    print(pts.describe(code))
"""

from . import codec, conditions, nodes, tools
from .character import Character
from .codec import backend_name, compress, decode, decompress, encode
from .errors import (
    BackendNotFoundError,
    InvalidCharacterCodeError,
    PythonshenanigansError,
)
from .tools import describe, dumps
from .types import (
    Animations,
    AwakeningType,
    BaseSkill,
    ChaseType,
    GenericSkill,
    MeleeType,
    SkillType,
    SpecialType,
)
from .utils import Branch, Properties

__version__ = "1.1.0"

__all__ = [
    "Animations",
    "AwakeningType",
    "BackendNotFoundError",
    "BaseSkill",
    "Branch",
    "Character",
    "ChaseType",
    "GenericSkill",
    "InvalidCharacterCodeError",
    "MeleeType",
    "Properties",
    "PythonshenanigansError",
    "SkillType",
    "SpecialType",
    "__version__",
    "backend_name",
    "codec",
    "compress",
    "conditions",
    "decode",
    "decompress",
    "describe",
    "dumps",
    "encode",
    "nodes",
    "tools",
]
