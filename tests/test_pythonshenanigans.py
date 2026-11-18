"""Tests for pythonshenanigans.

The fixtures are real character codes: one produced by the live game's editor
(it exercises every node, condition and property) and one from libjjs's README.
"""

import base64
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
    # unconfirmed PARTICLE settings still pass through verbatim
    assert nodes.PARTICLE(ID=1) == {"K_NAME": "PARTICLE", "ID": 1}
    assert nodes.LOOK() == {"K_NAME": "LOOK", "SMOOTHNESS": 40, "LAST HIT": -1}
    assert nodes.SETMELEE(combo=0) == {"K_NAME": "SETMELEE", "LAST HIT": -1, "COMBO": 0}
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
    assert sorted(keys) == [1, 2, 3, 4]


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


def test_visual_alt_fields_have_independent_defaults():
    """The docs are explicit: Alt Color 255,255,255 | Alt Size 1 | Alt Pos 0."""
    node = nodes.VISUAL(color="1, 2, 3", size=4, position=[1, 2, 3])
    assert node["COLOR"] == "1, 2, 3"
    assert node["ALT COLOR"] == "255, 255, 255"
    assert node["ALT SIZE"] == 1
    assert node["ALT POSITION"] == "0, 0, 0"


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


def test_documented_defaults_match_the_game():
    """Values taken from the game's own block descriptions."""
    assert nodes.SOUND()["VOLUME"] == 0.5
    assert conditions.HAS_AWK_BAR()["AMOUNT"] == 5
    assert nodes.PROJECTILE()["POSITION"] == "0, 0, 4"
    assert nodes.LOOK()["SMOOTHNESS"] == 40
    assert nodes.SETMELEE()["LAST HIT"] == -1


def test_newly_documented_fields_are_emitted():
    assert nodes.HITBOX(link_user=True)["LINK USER"] is True
    assert nodes.PROJECTILE(single_target=False)["SINGLE TARGET"] is False
    assert nodes.COUNTER(reflect=True)["REFLECT"] is True
    assert nodes.COUNTER(continue_=True)["CONTINUE"] is True
    assert nodes.TELEPORT(ignore_walls=True)["IGNORE WALLS"] is True
    assert nodes.ADD_HEALTH(can_kill=True)["CAN KILL"] is True
    assert nodes.STATE(state_tag="mytag")["STATE TAG"] == "mytag"


def test_look_setmelee_particle_builders():
    look = nodes.LOOK(time=1, horizontal_only=True, camera_direction=True)
    assert look["TIME"] == 1
    assert look["SMOOTHNESS"] == 40
    assert look["HORIZONTAL ONLY"] is True
    assert "GROUNDED" not in look  # unknown defaults are omitted, not guessed

    melee = nodes.SETMELEE(combo=-1, offset=2)
    assert melee == {"K_NAME": "SETMELEE", "LAST HIT": -1, "COMBO": -1, "OFFSET": 2}

    particle = nodes.PARTICLE(part_size=[1, 1, 1], emit_count=10, color="1,2,3")
    assert particle["PART SIZE"] == "1, 1, 1"
    assert particle["EMIT COUNT"] == 10
    assert particle["COLOR"] == "1,2,3"
    assert "RATE" not in particle
    assert "DURATION" not in particle
    # settings with no confirmed key pass through verbatim
    assert nodes.PARTICLE(**{"TRANSPARENCY": "0, 1"})["TRANSPARENCY"] == "0, 1"


FIXTURE = Path(__file__).parent / "fixtures" / "game_code_particle_look_setmelee.txt"


def _game_code() -> str:
    return FIXTURE.read_text(encoding="utf-8").strip()


def test_parses_a_game_code_using_particle_look_setmelee():
    payload = codec.decode(_game_code())
    assert len(payload) == 8

    kinds = set()
    for skill in payload:
        if isinstance(skill.get("DATA"), str):
            kinds.update(n["K_NAME"] for n in json.loads(skill["DATA"])["Line"])
    assert {"PARTICLE", "LOOK", "SETMELEE"} <= kinds

    rebuilt = pts.Character.from_code(_game_code()).export_character_code()
    assert codec.decode(rebuilt) == payload


def test_new_builders_use_exactly_the_game_keys():
    """Every key we emit must exist in the game's node: no typos, no extras."""
    game: dict[str, set[str]] = {}
    for skill in codec.decode(_game_code()):
        if isinstance(skill.get("DATA"), str):
            for node in json.loads(skill["DATA"])["Line"]:
                game.setdefault(node["K_NAME"], set()).update(node)

    full_look = nodes.LOOK(
        time=1,
        smoothness=5,
        horizontal_only=True,
        last_hit=2,
        relative_from_branch=True,
        projectile_tag="t",
        camera_direction=True,
        grounded=True,
    )
    assert set(full_look) == game["LOOK"]

    assert set(nodes.SETMELEE(combo=1, offset=2, last_hit=3)) == game["SETMELEE"]

    full_particle = nodes.PARTICLE(
        part_size=[1, 1, 1],
        texture=1,
        emit_count=2,
        rate=3,
        duration=4,
        color="1,2,3",
        size="1, 2",
        brightness=5,
        projectile_tag="t",
        last_hit=6,
    )
    assert set(full_particle) == game["PARTICLE"]


def test_game_code_shows_hiding_is_property_driven():
    payload = codec.decode(_game_code())

    def named(prefix):
        return next(s for s in payload if (s.get("NAME") or "").startswith(prefix))

    # Same KEY, different visibility: the properties decide, not the key.
    visible = named("visible skill")
    assert visible["KEY"] == 99
    assert "DATA" not in visible

    invisible = json.loads(named("invisible skill")["DATA"])["Prop"]
    assert invisible == {"AWK": True, "AWK2": True}

    # A single flag hides it in one mode only.
    assert json.loads(named("half-visible")["DATA"])["Prop"] == {"AWK2": True}


ALL_FIELDS_FIXTURE = (
    Path(__file__).parent / "fixtures" / "game_code_all_fields.txt"
)


def _all_fields_nodes() -> dict[str, set[str]]:
    """Every key the game wrote, grouped by node kind."""
    out: dict[str, set[str]] = {}
    for skill in codec.decode(ALL_FIELDS_FIXTURE.read_text(encoding="utf-8")):
        if isinstance(skill.get("DATA"), str):
            for node in json.loads(skill["DATA"])["Line"]:
                out.setdefault(node["K_NAME"], set()).update(node)
    return out


def test_every_key_the_game_emits_is_modelled():
    """A node must not be missing a field the game itself writes."""
    game = _all_fields_nodes()

    ours = {
        "PARTICLE": nodes.PARTICLE(
            part_size=[1, 1, 1],
            texture=1,
            emit_count=2,
            rate=3,
            duration=4,
            color="1,2,3",
            size=[1, 2],
            brightness=5,
            transparency=[1, 2],
            squash=[1, 2],
            lifetime=[1, 2],
            speed=[1, 2],
            rotation=[1, 2],
            rot_speed=[1, 2],
            acceleration=[1, 2, 3],
            drag=6,
            light_emission=7,
            light_influence=8,
            z_offset=9,
            spread_angle=[1, 2, 3],
            position=[1, 2, 3],
            lock_to_part=True,
            limb="Head",
            orientation_type="FacingCamera",
            emission_direction="Left",
            flipbook_size=[1, 2],
            flipbook_mode="Loop",
            flipbook_framerate=[1, 2],
            shape="Box",
            shape_inout="InAndOut",
            shape_partial=1,
            run_on_server=True,
            client_sided=True,
            cancel_tag="t",
            cancel=True,
            cancel_on_interrupt=True,
            projectile_tag="p",
            last_hit=1,
        ),
        "HITBOX": nodes.HITBOX(
            position=[1, 2, 3],
            rotation=[4, 5, 6],
            size=[7, 8, 9],
            stun=10,
            damage=11,
            debree=12,
            attack_type="Domain",
            blockable=True,
            blockable_360=True,
            cancel_enemy=True,
            clear_knockback=True,
            can_kill=True,
            hit_ragdoll=True,
            hit_user=True,
            single_target=False,
            branch="b",
            branch_target="t",
            branch_finisher="f",
            projectile_tag="p",
            link_user=True,
            preview=[0, 15],
            stun_anim=True,
            ignore_wakeup=True,
        ),
        "COUNTER": nodes.COUNTER(
            attack_type=["Melee", "Domain"],
            stun=2,
            branch="b",
            branch_target="t",
            reflect=True,
            continue_=True,
        ),
        "STATE": nodes.STATE(
            time=2,
            cancel_on_end=True,
            disable_burst=True,
            last_hit=3,
            check=True,
            branch="b",
            state_tag="t",
        ),
        "HPGIB": nodes.ADD_HEALTH(1, can_kill=True),
        "TELEPORT": nodes.TELEPORT(
            position=[1, 2, 3],
            rotation=[4, 5, 6],
            last_hit=7,
            projectile_tag="p",
            relative_from_branch=True,
            ignore_walls=True,
        ),
    }

    for kind, node in ours.items():
        missing = game[kind] - set(node)
        assert not missing, f"{kind} is missing game keys: {sorted(missing)}"

    # PARTICLE is fully modelled now, so the key sets must match exactly.
    assert set(ours["PARTICLE"]) == game["PARTICLE"]


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


# --------------------------------------------------------------------------- #
# remaining branches: unknown names, prefixes, backend selection, bad DATA
# --------------------------------------------------------------------------- #
def test_unknown_node_and_condition_names_pass_through():
    """_strip_*_defaults returns early when a K_NAME has no default table."""
    character = pts.Character()
    character.create.skill(
        "Unknown",
        [{"K_NAME": "NOT_A_REAL_NODE", "X": 1}],
        conditions=[{"K_NAME": "NOT_A_REAL_CONDITION", "Y": 2}],
    )
    data = json.loads(character.raw[0]["DATA"])
    assert data["Line"] == [{"K_NAME": "NOT_A_REAL_NODE", "X": 1}]
    assert data["Req"] == [{"K_NAME": "NOT_A_REAL_CONDITION", "Y": 2}]


def test_non_list_payloads_are_rejected_everywhere():
    not_a_list = {"NAME": "not a list"}
    with pytest.raises(pts.InvalidCharacterCodeError):
        pts.Character(raw=not_a_list)
    with pytest.raises(pts.InvalidCharacterCodeError):
        pts.Character.from_raw('{"NAME": "not a list"}')
    with pytest.raises(pts.InvalidCharacterCodeError):
        pts.Character.from_code(codec.encode(not_a_list))


def test_unknown_skill_kind_raises():
    with pytest.raises(ValueError, match="unknown skill kind"):
        pts.Character().create.skill("x", [nodes.WAIT()], kind="BOGUS")


def test_kind_specific_fields_and_extra():
    character = pts.Character()
    character.create.skill("added", [nodes.WAIT()], add=True)
    character.create.skill("spec", [nodes.WAIT()], kind="SPECIAL", cooldown=7)
    character.create.skill("chase", [nodes.WAIT()], kind="CHASE", cooldown=8)
    character.create.skill(
        "awk", [nodes.WAIT()], kind="AWAKENING", duration=15, delay=2
    )
    character.create.skill("extra", [nodes.WAIT()], extra={"SOMETHING": "new"})

    added, spec, chase, awakening, extra = character.raw
    assert added["ADD"] is True
    assert spec["COOLDOWN"] == 7
    assert chase["COOLDOWN"] == 8
    assert (awakening["DURATION"], awakening["DELAY"]) == (15, 2)
    assert extra["SOMETHING"] == "new"


def test_non_string_codes_are_rejected():
    with pytest.raises(pts.InvalidCharacterCodeError, match="expected a string"):
        codec.decode(123)


def test_codes_with_a_prefix_or_padding_are_resynced():
    code = codec.encode([{"K_NAME": "SPECIAL", "NAME": "x", "DATA": "{}"}])
    assert codec.decode(f"Code: {code}")[0]["NAME"] == "x"
    assert codec.decode(f"\n\n  {code}  \n")[0]["NAME"] == "x"


def test_corrupt_zstd_frames_are_rejected():
    """The underlying zstd error differs per backend; the type must not."""
    corrupt = base64.b64encode(codec.ZSTD_MAGIC + b"\x00\x01\x02\x03").decode()
    with pytest.raises(pts.InvalidCharacterCodeError):
        codec.decode(corrupt)


def test_frame_that_decompresses_to_nothing_is_rejected():
    # zstandard yields b"" for some corrupt frames instead of raising.
    with pytest.raises(pts.InvalidCharacterCodeError, match="no data"):
        codec.decode(codec.compress(""))


def test_payload_that_is_not_json_is_rejected():
    with pytest.raises(pts.InvalidCharacterCodeError, match="not valid JSON"):
        codec.decode(codec.compress("this is not json"))


def test_missing_backends_report_what_was_tried(monkeypatch):
    def broken():
        raise ImportError("nope")

    monkeypatch.setattr(codec, "_BACKENDS", (("alpha", broken), ("beta", broken)))
    with pytest.raises(pts.BackendNotFoundError, match="no usable zstd backend"):
        codec._load_backend()


def test_preferred_backend_is_tried_first(monkeypatch):
    def make(name):
        return lambda: codec._Backend(name, lambda b: b, lambda b: b)

    monkeypatch.setattr(
        codec,
        "_BACKENDS",
        (("alpha", make("alpha")), ("zstandard", make("zstandard"))),
    )

    monkeypatch.setenv(codec.ENV_BACKEND, "zstandard")
    assert codec._load_backend().name == "zstandard"

    monkeypatch.setenv(codec.ENV_BACKEND, "")
    assert codec._load_backend().name == "alpha"


def test_zstd_backend_loader_uses_the_zstd_module(monkeypatch):
    """`zstd` is uninstallable from PyPI, so exercise the loader with a stub."""
    import types

    fake = types.ModuleType("zstd")
    fake.compress = lambda data: b"compressed:" + data
    fake.decompress = lambda data: data.removeprefix(b"compressed:")
    monkeypatch.setitem(sys.modules, "zstd", fake)

    backend = codec._backend_zstd()
    assert backend.name == "zstd"
    assert backend.compress(b"hi") == b"compressed:hi"
    assert backend.decompress(b"compressed:hi") == b"hi"


def test_dumps_tolerates_data_that_is_not_json():
    payload = [{"NAME": "x", "K_NAME": "SKILL", "KEY": 1, "DATA": "not json"}]
    expanded = json.loads(pts.dumps(codec.encode(payload)))
    assert expanded[0]["DATA"] == "not json"


def test_describe_rejects_non_lists_and_tolerates_bad_data():
    with pytest.raises(pts.InvalidCharacterCodeError):
        pts.describe(codec.encode({"not": "a list"}))

    payload = [{"NAME": "x", "K_NAME": "SKILL", "DATA": "not json"}]
    info = pts.describe(codec.encode(payload))
    assert info["skills"][0]["name"] == "x"
    assert "nodes" not in info["skills"][0]


def test_builders_honour_explicitly_supplied_vectors():
    """The other side of every ``None`` guard in nodes.py."""
    assert nodes.VELOCITY(force=[1, 2, 3])["FORCE"] == "1, 2, 3"

    hitbox = nodes.HITBOX(position=[1, 1, 1], rotation=[2, 2, 2], size=[3, 3, 3])
    assert (hitbox["POSITION"], hitbox["ROTATION"], hitbox["SIZE"]) == (
        "1, 1, 1",
        "2, 2, 2",
        "3, 3, 3",
    )

    grab = nodes.GRAB(position=[1, 1, 1], rotation=[2, 2, 2])
    assert (grab["POSITION"], grab["ROTATION"]) == ("1, 1, 1", "2, 2, 2")

    projectile = nodes.PROJECTILE(
        position=[1, 1, 1], rotation=[2, 2, 2], size=[3, 3, 3]
    )
    assert (
        projectile["POSITION"],
        projectile["ROTATION"],
        projectile["SIZE"],
    ) == ("1, 1, 1", "2, 2, 2", "3, 3, 3")

    teleport = nodes.TELEPORT(position=[1, 1, 1], rotation=[2, 2, 2])
    assert (teleport["POSITION"], teleport["ROTATION"]) == ("1, 1, 1", "2, 2, 2")

    visual = nodes.VISUAL(
        position=[1, 1, 1],
        rotation=[2, 2, 2],
        alt_position=[3, 3, 3],
        alt_rotation=[4, 4, 4],
    )
    assert (visual["POSITION"], visual["ROTATION"]) == ("1, 1, 1", "2, 2, 2")
    assert (visual["ALT POSITION"], visual["ALT ROTATION"]) == ("3, 3, 3", "4, 4, 4")

    assert nodes.ANIMATION([1, 5])["ANIM_USE"] == [1, 5]
    assert nodes.COUNTER(["Bullet"])["ATTACK TYPE2"] == "Bullet"


def test_melee_kind_and_none_cooldowns():
    character = pts.Character()
    character.create.skill("melee", [nodes.WAIT()], kind="MELEE")
    character.create.skill("spec", [nodes.WAIT()], kind="SPECIAL", cooldown=None)
    character.create.skill("chase", [nodes.WAIT()], kind="CHASE", cooldown=None)
    character.create.skill("plain", [nodes.WAIT()], cooldown=None)

    melee, spec, chase, plain = character.raw
    assert "COOLDOWN" not in melee  # MELEE takes neither COOLDOWN nor KEY
    assert "KEY" not in melee
    for skill in (spec, chase, plain):
        assert "COOLDOWN" not in skill
    assert plain["KEY"] == 1


def test_dumps_can_leave_data_unexpanded():
    character = pts.Character()
    character.create.skill("x", [nodes.WAIT(0.5)])
    code = character.export_character_code()

    raw_view = json.loads(pts.dumps(code, expand_data=False))
    assert isinstance(raw_view[0]["DATA"], str)

    expanded = json.loads(pts.dumps(code))
    assert isinstance(expanded[0]["DATA"], dict)


def test_describe_handles_skills_without_branches():
    character = pts.Character()
    character.create.skill("x", [nodes.WAIT(0.5)])
    info = pts.describe(character.export_character_code())
    assert info["skills"][0]["nodes"] == ["WAIT"]
    assert "branches" not in info["skills"][0]
