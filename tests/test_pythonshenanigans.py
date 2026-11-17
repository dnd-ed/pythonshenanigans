"""Tests for pythonshenanigans.

The fixtures are real character codes: one produced by the live game's editor
(it exercises every node, condition and property) and one from libjjs's README.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import pythonshenanigans as pts
from pythonshenanigans import codec, nodes

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


@pytest.mark.parametrize("bad", ["", "not base64!!", "aGVsbG8="])
def test_invalid_codes_raise(bad):
    with pytest.raises(pts.InvalidCharacterCodeError):
        codec.decode(bad)
