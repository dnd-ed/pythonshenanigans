"""Tests for pythonshenanigans.

The fixtures are real character codes: one produced by the live game's editor
(it exercises every node, condition and property) and one from libjjs's README.
"""

import inspect
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import pythonshenanigans as pts
from pythonshenanigans import codec, conditions, nodes

# Made by the game's editor: 5 skills, every node/condition/property, and the
# PARTICLE/LOOK/SETMELEE nodes plus TOOL TIP / COLOR / PREVIEW fields that
# libjjs did not model.
SAMPLE_CODE = (
    "KLUv/WBQDiUXAKafYSYgjegBBJM6aoiXqjHhyQ+trFwcIU39Gj2yvQsXPisOjRCqBIBkQFgAVgBXAD51dp3zJcusySU7Nwri"
    "OkdYdqHzxXWWRCZVxdH50q79OuzWVsWSLCAuC0ahWNp1jXchKb3dGNcJ/3RrKeMTKTzd2nqoJhh2OUi064d8drMksIrBNYTe"
    "F0jWq6X15d/rN3r4tX8npu9lvO8PqK0Otw/pOIqS86ZbB3Xc6DDv56SPypcQDCKKaQzEdf4IK7TOUJzeqIag0QQINAYYBQ2AQGNA"
    "XOfpo/S2enxfW9b5xv7olGZsqCyWSXVVKgrrkq3/D4PBPI/OJ+CZfOIb0flM3rlZExULBKVSoaTOjA5R6GBo3XElhqJXCB/Y6I3"
    "KOv/Lh+5HT6VUwnc/evPd6Ehfnfi4Er94A1TWH7nzJCpJpGFZmPXQ2QW7Jo+lS01rWrNgGtOYdm2ppFw+7NaPGec/PrlDRdUwrie"
    "N1y3u6opYEJeWMVzPiUJJ6evWWda5eUCwvnWuP5z0Iyz/zYCFqLEVckrRSBhJQSvLGjACQpghEqoHEkAAQRCiYJahMEQxJCSKDc0E"
    "5VdazQEQ2zqb1N+FHz8Z8CnreYoF69cecwna25vjCseKbv97HwmeSpF8fBWFSd6G8XzvyIvhjLa28dXEsoCGLpFSjb5ODEeKoEJW"
    "wHO+bBC2dJZjCXqlRBdCQ0nwEN/d+NgVJLQHgcITIGB//kXHT9CZvMuBnhsM13tNnJ6uMBNXE2eaR904AB7KF9ysyPtr2WZHs2ON"
    "Pn6R82VXKioqRtFR5A6RzXsq0q7iSKL9bU5EIm5ylpaPIasmOTEDDo0j9nTxaeKj6AEVGO+OOaAd0OnxIsG62iEFJwki9tSjJnDG"
    "v9z59VRdA33D6UJRxQIwZTJPmcfffgMIZDF2wcj8cKkaEBZnu00dJGaidoZopRJTQVJhd/b0Qqw1Ldoe58l1ikDxIok8/FYjVgHy"
    "g8cVsc7V"
)

# From libjjs's README.
LIBJJS_README_CODE = (
    "KLUv/WCJA40PALZaVSYQq+oBsOM43sl9eKAChX7vhegbSNzqodFpbd8lezRGBFEAAAAAOEcASQBOAJ03z8REfJoIHQUUIeRA2V"
    "minb3zQON2lp3zdsnO2YVSO28t+/FL7VA2wXS0d63UcQ0c7V2ZYJr2LXs+3rZnDRbsQLYkfW9XPzAxMA2IsvME+MdLjvPn/NmJYnon"
    "KuH8cf4U0NsZ07eeiHgUS6LDS3aeF2LwoPYf1L5LIoQRchZQ0zTweU9EPH+X7GxNGpkVFQ/XVSYUB4G3eSbKttYk1WmK2jujgGG4ZO"
    "eFrOrsEsdpYlRAT7NQLKCEAxHQExowS8NVJpiFgaPZaMzOjmmAw/drfcilEefF2FRTnSKHa5LMBUPRMO2CTS6U4OuU2hvAUjsdb/1"
    "E8VcQqTfPtOzMgUGTneuM7EedHULqFMkX26fVR9ysjLfTchkFAYOJJnVpNKn73pzUbQUsPCAwQmKUdHZDsOFRRQGDZJeg4u6FMgn9"
    "G4xiAPIHGdrNOg4s5CTYCMJiCAp+76pl4PKqVSgDF8iWuV4akML0PQhEMn2ZxDIoECGsfoU0I8XsfY4F7awNkGkx71XcGk5v2o65y"
    "PltaZAXHDe2ACCX8IZgO6luOUUiiHldxh0CwYHoazqecXAVjSR5gj3dmmrpkHIMI2aSyjgZ"
)


def test_backend_is_detected():
    assert pts.backend_name()


def test_backend_can_be_forced_with_env_var():
    """PYTHONSHENANIGANS_ZSTD_BACKEND must win over the default order."""
    from importlib.util import find_spec

    src = Path(__file__).resolve().parents[1] / "src"
    for backend, module in (
        ("pyzstd", "pyzstd"),
        ("zstandard", "zstandard"),
        ("compression.zstd", "compression.zstd"),
    ):
        try:
            available = find_spec(module) is not None
        except (ImportError, ModuleNotFoundError):
            available = False
        if not available:
            continue

        env = dict(
            os.environ,
            PYTHONSHENANIGANS_ZSTD_BACKEND=backend,
            PYTHONPATH=str(src),
        )
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import pythonshenanigans as p; print(p.backend_name())",
            ],
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == backend
        return
    pytest.skip("no zstd backend installed to force")


def test_decode_libjjs_readme_sample():
    payload = codec.decode(LIBJJS_README_CODE)
    assert isinstance(payload, list)
    assert [s["K_NAME"] for s in payload] == ["SKILL", "SPECIAL", "AWAKENING"]


def test_roundtrip_preserves_everything():
    original = codec.decode(SAMPLE_CODE)
    rebuilt = pts.Character.from_code(SAMPLE_CODE).export_character_code()
    assert codec.decode(rebuilt) == original


def test_unmodelled_fields_survive_roundtrip():
    payload = codec.decode(
        pts.Character.from_code(SAMPLE_CODE).export_character_code()
    )
    assert payload[0]["TOOL TIP"] == "tooltip here"
    assert payload[2]["COLOR"] == "1,1,1 5,5,5"
    kinds = [n["K_NAME"] for n in json.loads(payload[0]["DATA"])["Line"]]
    for kind in ("PARTICLE", "LOOK", "SETMELEE"):
        assert kind in kinds


def test_new_node_builders():
    assert nodes.PARTICLE(ID=1) == {"K_NAME": "PARTICLE", "ID": 1}
    assert nodes.LOOK() == {"K_NAME": "LOOK"}
    assert nodes.SETMELEE(**{"A B": 2}) == {"K_NAME": "SETMELEE", "A B": 2}
    assert nodes.raw("CUSTOM", X=1) == {"K_NAME": "CUSTOM", "X": 1}


def test_hitbox_preview_field():
    assert nodes.HITBOX(preview=[0, 15])["PREVIEW"] == [0, 15]
    assert "PREVIEW" not in nodes.HITBOX()


def test_auto_keys_do_not_collide():
    character = pts.Character(hide_character_extras=True)
    for index in range(3):
        character.create.skill(f"skill{index}", [nodes.WAIT()])
    keys = [s["KEY"] for s in character.raw if s.get("K_NAME") == "SKILL"]
    assert len(keys) == len(set(keys))
    assert sorted(keys) == [0, 1, 2, 3]


def test_tooltip_and_color_are_emitted():
    character = pts.Character()
    character.create.skill("a", [nodes.WAIT()], tooltip="hi")
    character.create.skill("b", [], kind="AWAKENING", color="1,1,1 2,2,2")
    assert character.raw[0]["TOOL TIP"] == "hi"
    assert character.raw[1]["COLOR"] == "1,1,1 2,2,2"


def test_skill_without_line_is_allowed():
    # The README's usage example calls this without a node list.
    character = pts.Character()
    character.create.skill(name="Super Cool Skill", cooldown=5)
    skill = character.raw[0]
    assert skill["KEY"] == 1
    assert skill["COOLDOWN"] == 5
    assert json.loads(skill["DATA"])["Line"] == []


def test_key_auto_continues_from_loaded_character():
    character = pts.Character.from_code(SAMPLE_CODE)
    character.create.skill("new", [nodes.WAIT()])
    assert character.raw[-1]["KEY"] == 2  # the sample's only SKILL already used 1


def test_describe():
    info = pts.describe(SAMPLE_CODE)
    assert info["skill_count"] == 5
    assert info["skills"][4]["kind"] == "CHASE"


SEQUENCE_NODE_BUILDERS = [
    nodes.ANIMATION,
    nodes.VELOCITY,
    nodes.HITBOX,
    nodes.VISUAL,
    nodes.GRAB,
    nodes.PROJECTILE,
    nodes.COUNTER,
    nodes.TELEPORT,
]


def test_no_node_builder_has_a_mutable_parameter_default():
    """A list/dict literal as a parameter default is shared across all calls."""
    offenders = []
    for name, obj in vars(nodes).items():
        if not inspect.isfunction(obj) or obj.__module__ != nodes.__name__:
            continue
        for parameter, spec in inspect.signature(obj).parameters.items():
            if isinstance(spec.default, (list, dict, set)):
                offenders.append(f"{name}({parameter}={spec.default!r})")
    assert offenders == []


@pytest.mark.parametrize("builder", SEQUENCE_NODE_BUILDERS)
def test_nodes_never_share_state_between_calls(builder):
    first, second = builder(), builder()

    shared = [
        key
        for key, value in first.items()
        if isinstance(value, (list, dict, set)) and value is second[key]
    ]
    assert shared == [], f"{builder.__name__} shares {shared} between calls"

    for key, value in first.items():
        if isinstance(value, list):
            value.append("sentinel")
            assert "sentinel" not in second[key]


def test_anim_defaults_are_actually_stripped():
    # Regression: _NODE_BUILDERS was keyed "ANIMATION" while the node's K_NAME is
    # "ANIM", so ANIM defaults were never stripped.
    character = pts.Character()
    character.create.skill("anim", [nodes.ANIMATION()])
    node = json.loads(character.raw[0]["DATA"])["Line"][0]
    assert node == {"K_NAME": "ANIM"}


def test_anim_keeps_non_default_values():
    character = pts.Character()
    character.create.skill("anim", [nodes.ANIMATION([1, 5])])
    node = json.loads(character.raw[0]["DATA"])["Line"][0]
    assert node["ANIM_USE"] == [1, 5]


def test_visual_alt_fields_fall_back_to_the_main_value():
    node = nodes.VISUAL(color="1, 2, 3", size=4)
    assert node["ALT COLOR"] == "1, 2, 3"
    assert node["ALT SIZE"] == 4


def test_generated_frames_are_single_segment_like_the_game():
    """Frames we emit declare the content size, exactly like the game's own."""
    import base64

    def is_single_segment(blob: bytes) -> bool:
        assert blob[:4] == codec.ZSTD_MAGIC
        return bool((blob[4] >> 5) & 1)

    game = base64.b64decode(
        LIBJJS_README_CODE + "=" * (-len(LIBJJS_README_CODE) % 4)
    )
    generated = base64.b64decode(codec.compress('{"a": 1}'))

    assert is_single_segment(game) is True
    assert is_single_segment(generated) is True


def test_node_builder_keys_match_their_k_names():
    """Guards the ANIM bug class: a `_NODE_BUILDERS` key must equal its K_NAME."""
    from pythonshenanigans.defaults import _NODE_BUILDERS

    mismatches = {}
    for key, builder in _NODE_BUILDERS.items():
        k_name = getattr(nodes, builder)()["K_NAME"]
        if k_name != key:
            mismatches[key] = k_name
    assert mismatches == {}


def test_version_matches_pyproject():
    import tomllib

    root = Path(__file__).resolve().parents[1]
    declared = tomllib.loads(
        (root / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]["version"]
    assert pts.__version__ == declared


def test_vec3_accepts_any_iterable():
    assert nodes.HITBOX(position=(1, 2, 3))["POSITION"] == "1, 2, 3"
    assert nodes.TELEPORT(position=[4, 5, 6])["POSITION"] == "4, 5, 6"


def test_vec3_passes_preformatted_strings_through():
    # The game, dumps() and describe() all express vectors as "x, y, z".
    assert nodes.HITBOX(position="1, 2, 3")["POSITION"] == "1, 2, 3"
    assert nodes.TELEPORT(rotation="4, 5, 6")["ROTATION"] == "4, 5, 6"
    # a copy-pasted list literal is tolerated
    assert nodes.HITBOX(position="[1, 2, 3]")["POSITION"] == "1, 2, 3"


def test_vector_strings_from_a_decoded_code_round_trip():
    """Regression: feeding a decoded "x, y, z" string back into a builder."""
    line = json.loads(codec.decode(LIBJJS_README_CODE)[0]["DATA"])["Line"]
    hitbox = next(node for node in line if node["K_NAME"] == "HITBOX")
    assert hitbox["POSITION"] == "0, 0, 3"  # a real game-produced vector
    rebuilt = nodes.HITBOX(position=hitbox["POSITION"], size=hitbox["SIZE"])
    assert rebuilt["POSITION"] == hitbox["POSITION"]
    assert rebuilt["SIZE"] == hitbox["SIZE"]


def test_create_raw_skill_rejects_non_dicts():
    character = pts.Character()
    with pytest.raises(pts.InvalidCharacterCodeError):
        character.create_raw_skill("not a dict")
    assert len(character) == 0

    character.create_raw_skill({"NAME": "n", "K_NAME": "SPECIAL", "DATA": "{}"})
    reloaded = pts.Character.from_code(character.export_character_code())
    assert reloaded.raw == character.raw


def test_visual_alt_positions_fall_back_to_the_main_value():
    node = nodes.VISUAL(position=[1, 2, 3], rotation=[4, 5, 6])
    assert node["POSITION"] == "1, 2, 3"
    assert node["ALT POSITION"] == "1, 2, 3"
    assert node["ALT ROTATION"] == "4, 5, 6"


def test_bad_payload_entries_raise_invalid_character_code():
    """A structurally wrong payload must not leak AttributeError."""
    with pytest.raises(pts.InvalidCharacterCodeError):
        pts.Character.from_code(codec.encode([1, 2, 3]))
    with pytest.raises(pts.InvalidCharacterCodeError):
        pts.Character.from_raw("[1, 2, 3]")
    with pytest.raises(pts.InvalidCharacterCodeError):
        pts.Character(raw=[1, 2, 3])
    with pytest.raises(pts.InvalidCharacterCodeError):
        pts.Character.from_raw("{not json")


def test_to_code_is_an_alias_for_export_character_code():
    character = pts.Character()
    character.create.skill("Alias", [nodes.WAIT(1)])
    assert character.to_code() == character.export_character_code()


def test_from_raw_and_create_raw_skill():
    character = pts.Character()
    character.create.skill("Raw", [nodes.WAIT(0.5)])

    reloaded = pts.Character.from_raw(character.export_raw())
    assert reloaded.raw == character.raw
    assert reloaded.export_character_code() == character.export_character_code()

    reloaded.create_raw_skill(
        {"NAME": "handmade", "K_NAME": "SPECIAL", "DATA": "{}", "COOLDOWN": 0}
    )
    assert reloaded.skills[-1] == {"kind": "SPECIAL", "name": "handmade"}


def test_len_and_iter():
    character = pts.Character()
    character.create.skill("one", [nodes.WAIT()])
    character.create.skill("two", [nodes.WAIT()])
    assert len(character) == 2
    assert [s["NAME"] for s in character] == ["one", "two"]


def test_branch_builder():
    branch = pts.Branch([nodes.WAIT(0.25)], conditions=[conditions.IN_AIR()])
    assert branch["nodes"] == [{"K_NAME": "WAIT", "TIME": 0.25}]
    assert branch["conditions"] == [{"K_NAME": "AIR", "FLIP": False}]

    character = pts.Character()
    character.create.skill("Branchy", [nodes.WAIT()], branches={"b": branch})
    data = json.loads(character.raw[0]["DATA"])
    assert set(data["Branch"]) == {"b"}
    assert data["Branch"]["b"]["Req"] == [{"K_NAME": "AIR"}]


def test_properties_defaults_are_stripped():
    character = pts.Character()
    character.create.skill("default", [nodes.WAIT()], properties=pts.Properties())
    character.create.skill(
        "custom", [nodes.WAIT()], properties=pts.Properties(damage_multiplier=3)
    )
    assert json.loads(character.raw[0]["DATA"])["Prop"] == {}
    assert json.loads(character.raw[1]["DATA"])["Prop"] == {"DMG": 3}


def test_dumps_expands_the_node_graph():
    character = pts.Character()
    character.create.skill("Expandable", [nodes.WAIT(0.5)])
    expanded = json.loads(pts.dumps(character.export_character_code()))
    assert expanded[0]["DATA"]["Line"][0]["K_NAME"] == "WAIT"


def test_nested_data_strings_are_expanded_recursively():
    """_expand used to leave a DATA string nested inside a parsed DATA."""
    inner = json.dumps({"Line": [], "Req": [], "Prop": {}})
    middle = json.dumps(
        {"Line": [], "Req": [], "Prop": {}, "Nested": {"DATA": inner}}
    )
    payload = [{"NAME": "x", "K_NAME": "SKILL", "KEY": 1, "DATA": middle}]
    expanded = json.loads(pts.dumps(codec.encode(payload)))
    assert isinstance(expanded[0]["DATA"]["Nested"]["DATA"], dict)


def test_error_hierarchy():
    assert issubclass(pts.InvalidCharacterCodeError, pts.PythonshenanigansError)
    assert issubclass(pts.InvalidCharacterCodeError, ValueError)
    assert issubclass(pts.BackendNotFoundError, pts.PythonshenanigansError)
    assert issubclass(pts.BackendNotFoundError, ImportError)
    with pytest.raises(pts.PythonshenanigansError):
        codec.decode("obviously not a code!!")


def test_describe_handles_non_dict_entries():
    info = pts.describe(codec.encode([1, 2]))
    assert info["skill_count"] == 2


def test_every_condition_builder_serialises():
    built = [
        conditions.IN_AIR(),
        conditions.IS_JUMPING(flip=True),
        conditions.HAS_TARGET(),
        conditions.IS_AWAKENED(flip=True),
        conditions.HAS_AWK_BAR(3),
        conditions.DURABILITY(2),
        conditions.HAS_HEALTH(50, flip=True),
        conditions.IS_IN_DOMAIN(),
        conditions.IS_HOLDING(flip=True),
    ]
    character = pts.Character()
    character.create.skill("Cond", [nodes.WAIT()], conditions=built)
    req = json.loads(character.raw[0]["DATA"])["Req"]
    assert [c["K_NAME"] for c in req] == [
        "AIR",
        "JUMP",
        "AIM",
        "ULT",
        "BAR",
        "DUR",
        "HP",
        "DOMAIN",
        "HOLD",
    ]


@pytest.mark.parametrize(
    "loader",
    ["_backend_stdlib", "_backend_zstd", "_backend_pyzstd", "_backend_zstandard"],
)
def test_each_installed_backend_round_trips(loader):
    """Covers the loader bodies, not just whichever backend happens to be active."""
    try:
        backend = getattr(codec, loader)()
    except Exception as exc:  # not installed in this environment
        pytest.skip(f"{loader} unavailable: {exc}")

    payload = b"character code payload " * 20
    assert backend.decompress(backend.compress(payload)) == payload


@pytest.mark.parametrize("bad", ["", "not base64!!", "aGVsbG8="])
def test_invalid_codes_raise(bad):
    with pytest.raises(pts.InvalidCharacterCodeError):
        codec.decode(bad)
