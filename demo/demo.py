"""Demo for pythonshenanigans: build a moveset, then load it back.

Run with::

    python demo/demo.py
"""

import os
import sys

# Running from a source checkout (not an installed package): add src/ to path.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import pythonshenanigans as pts
import pythonshenanigans.conditions as conditions
import pythonshenanigans.nodes as nodes

# ------------------------------------------------------------------ building #
character = pts.Character(hide_character_extras=True)

# A faster Todo swap that only works while airborne.
character.create.skill(
    "Quick Swap",
    [nodes.SPECIAL("Boogie Woogie", 100, enable_variants=False)],
    kind="SPECIAL",
    cooldown=0,
    conditions=[conditions.IN_AIR()],
)

# A normal skill exercising a few node types, a tooltip and the extra nodes.
character.create.skill(
    "Blitz",
    [
        nodes.SET_COOLDOWN(-1, 2),
        nodes.STATE("SpeedMultiplier", 2, 2),
        nodes.VISUAL("Field of View", 140, time=2),
        nodes.HITBOX(size=[6, 6, 4], damage=5, preview=[0, 15]),
        nodes.WAIT(0.5),
        nodes.PARTICLE(**{"SPEED": 1}),
    ],
    cooldown=5,
    tooltip="A short dash with a particle burst.",
)

# An awakening with the game's start/end colour pair.
character.create.skill(
    "Awakening",
    [nodes.VISUAL("Shine", time=1)],
    kind="AWAKENING",
    duration=15,
    delay=1,
    color="1,1,1 5,5,5",
)

code = character.export_character_code()

print("zstd backend:", pts.backend_name())
print("character code:")
print(code)
print()

# ------------------------------------------------------------------ loading #
print("summary:")
for entry in pts.describe(code)["skills"]:
    print("  ", entry["kind"], "-", entry["name"], "->", entry.get("nodes"))
print()

print("pretty payload (DATA expanded):")
print(pts.dumps(code))
