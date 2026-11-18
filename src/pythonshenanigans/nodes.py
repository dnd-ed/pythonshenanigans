from collections.abc import Iterable
from typing import Literal

from .types import (
    AttackType,
    BodyParts,
    EasingDirections,
    EasingStyles,
    Effects,
    Skills,
    Specials,
    States,
)


def _vec3(value: Iterable[float] | str) -> str:
    """Format a vector as the game's ``"x, y, z"`` string.

    Accepts any iterable, *or* an already-formatted string. Strings must pass
    through verbatim: the game, ``dumps()`` and ``describe()`` all express
    vectors this way, so a vector copied out of a decoded code has to survive
    being handed straight back to a builder.
    """
    if isinstance(value, str):
        # Already "x, y, z"; tolerate a copy-pasted "[x, y, z]".
        return value.strip().strip("[]").strip()
    return ", ".join(str(component) for component in value)


def WAIT(TIME: float = 1):
    """Wait a duration of time before continuing.

    :param TIME: How many seconds to delay the next NODE by.
    """
    return {"K_NAME": "WAIT", "TIME": TIME}


def SKILL(
    move: Skills = "Divergent Fist",
    speed: float = 1,
    cancel_last: bool = False,
    enable_variants: bool = True,
    hold_for: float = 0,
    start: float = 0,
):
    """Run a base moveset skill.

    :param move: The skill to run. [no in-game documentation]
    :param speed: Multiplier of the Skill's speed.
    :param cancel_last: Cancels the previous NODE if set to true.
    :param enable_variants: Enable variants instead of only using the base variant. [no in-game documentation]
    :param hold_for: How many seconds to hold the skill for. Only applicable to holdable skills, such as Max Elephant.
    :param start: Where to begin the Skill from, starting from 0 seconds.
    """
    return {
        "K_NAME": "SKILL",
        "MOVE": move,
        "SPEED": speed,
        "START": start,
        "HOLD FOR": hold_for,
        "ENABLE VARIANTS": enable_variants,
        "CANCEL LAST": cancel_last,
    }


def SPECIAL(
    spec: Specials = "Limitless",
    speed: float = 1,
    cancel_last: bool = False,
    enable_variants: bool = True,
):
    """Run a base moveset special skill.

    :param spec: The special skill to run. [no in-game documentation]
    :param speed: Multiplier of the Skill's speed.
    :param cancel_last: Cancels the previous NODE if set to true.
    :param enable_variants: Enable variants instead of only using the base variant. [no in-game documentation]
    """
    return {
        "K_NAME": "SPECIAL",
        "SPEC": spec,
        "SPEED": speed,
        "ENABLE VARIANTS": enable_variants,
        "CANCEL LAST": cancel_last,
    }


# ANIM_USE seems to be in [character#, anim#] format, so this is gojo's hollowpurple
# hollow purple is the default cuz its [1,1] i guess
# use types.Animations tho pls
def ANIMATION(
    animation: list[float] | None = None,
    start: float = 0,
    end: float = 10,  # non-default, but whatever (ingame default changes per animation)
    looped: bool = False,
    speed: float = 1,
    fade_in: float = 0.1,
    fade_out: float = 0,
    last_hit: float = -1,
):
    """Play an animation.

    :param animation: The animation to play, use types.Animations for definitions. [no in-game documentation]
    :param start: The start time of the animation. [no in-game documentation]
    :param end: The end time of the animation. [no in-game documentation]
    :param looped: Loop the animation as long as the skill is active.
    :param speed: Multiplier of the Animation's speed.
    :param fade_in: How fast the Animation should fade in, in seconds.
    :param fade_out: How fast the Animation should fade out, in seconds.
    :param last_hit: Activates this NODE on a target hit in the last (value) seconds.
    """
    if animation is None:
        animation = [1, 1]
    return {
        "K_NAME": "ANIM",
        "ANIM_USE": animation,
        "PREVIEW": [start, end],
        "SPEED": speed,
        "FADE IN": fade_in,
        "FADE OUT": fade_out,
        "LAST HIT": last_hit,
        "LOOPED": looped,
    }


def SOUND(
    id: int = 12222253,
    speed: float = 1,
    volume: float = 0.5,
    start: float = 0,
    end: float = 500,
    fade_in: float = 0,
    fade_out: float = 0,
    cancel: bool = False,
    global_: bool = False,
    projectile_tag: str = "nil",
):
    """Play a sound effect.

    :param id: The sound's AssetID.
    :param speed: Multiplier of the Sound's playback speed.
    :param volume: Multiplier of the Sound's volume.
    :param start: Where to begin the Sound from, starting at 0 seconds.
    :param end: Where to end the Sound at, in seconds.
    :param fade_in: How fast the Animation should fade in, in seconds. [no in-game documentation]
    :param fade_out: How fast the Animation should fade out, in seconds. [no in-game documentation]
    :param cancel: Cancels all currently playing Sound NODEs.
    :param global_: Disables 3D falloff, playing the sound at the same volume for everyone.
    :param projectile_tag: The name of a projectile's tag. If matched with an existing projectile, the sound follows the projectile.
    """
    return {
        "K_NAME": "SFX",
        "ID": id,
        "START": start,
        "END": end,
        "SPEED": speed,
        "VOLUME": volume,
        "FADE IN": fade_in,
        "FADE OUT": fade_out,
        "GLOBAL": global_,
        "PROJECTILE TAG": projectile_tag,
        "CANCEL": cancel,
    }


def VELOCITY(
    force: list[float] | None = None,
    time: float | Literal["inf"] = 0,
    fade: bool = False,
    track: bool = False,
    last_hit: float = -1,
    ragdoll: float = 0,
    true_ragdoll: bool = False,
    relative_from_branch: bool = False,
):
    """Apply a force to a character.

    :param force: The direction where force should be applied towards. Higher values = bigger force (X, Y, Z)
    :param time: How long the force should be active for.
    :param fade: The force linearly fades to 0,0,0 over time,
    :param track: Force direction tracks the torso's orientation during the entire duration of the NODE.
    :param last_hit: Activates this NODE on a target hit in the last (value) seconds.
    :param ragdoll: If the value is above 0, ragdolls for (value) seconds.
    :param true_ragdoll: Disables ragdoll cancel.
    :param relative_from_branch: Force direction is relative to the Branch origin.
    """
    if force is None:
        force = [0, 0, 0]
    return {
        "K_NAME": "VELO",
        "FORCE": _vec3(force),
        "TIME": time,
        "FADE": fade,
        "TRACK": track,
        "LAST HIT": last_hit,
        "RAGDOLL": ragdoll,
        "TRUE RAGDOLL": true_ragdoll,
        "RELATIVE FROM BRANCH": relative_from_branch,
    }


def CONNECT(
    signal: str = "Nothing",
    time: float | Literal["inf"] = 0.1,
    range: float | Literal["inf"] = "inf",
):
    """Emits a signal to Connect Blocks.

    :param signal: The block's signal.
    :param time: How long the signal should be active for, in seconds.
    :param range: Activation range for the signal, in studs.
    """
    return {"K_NAME": "CONNECT", "SIGNAL": signal, "TIME": time, "RANGE": range}


def HITBOX(
    position: list[float] | None = None,
    rotation: list[float] | None = None,
    size: list[float] | None = None,
    stun: float = 1,
    stun_anim: bool = False,
    ignore_wakeup: bool = False,
    damage: float = 1,
    debree: int = 0,
    attack_type: AttackType = "Melee",
    blockable: bool = True,
    blockable_360: bool = False,
    cancel_enemy: bool = True,
    clear_knockback: bool = False,
    can_kill: bool = True,
    hit_ragdoll: bool = False,
    hit_user: bool = False,
    single_target: bool = True,
    branch: str = "nil",
    branch_target: str = "nil",
    branch_finisher: str = "nil",
    projectile_tag: str = "nil",
    link_user: bool = False,
    preview: list[float] | None = None,
):
    """Create a hitbox.

    :param position: The hitbox's position, the origin being the player's center. (X, Y, Z)
    :param rotation: The hitbox's rotation, relative to the player's orientation. (X, Y, Z)
    :param size: The size of the hitbox. (X, Y, Z)
    :param stun: How long the stun on hit should last for, in seconds.
    :param stun_anim: Plays a generic stun animation on the hit target.
    :param ignore_wakeup: Ignore the wakeup stun immunity (disable for accurate M1s).
    :param damage: How much damage should be dealt on hit.
    :param debree: If not 0, causes destruction. The value determines the Debree Fidelity, which is 2 by default. Negative values don't spawn debree.
    :param attack_type: The hitbox's attack type. [no in-game documentation]
    :param blockable: The hitbox is blockable from the front.
    :param blockable_360: The hitbox is blockable regardless of orientation.
    :param cancel_enemy: Cancels the hit target(s).
    :param clear_knockback: Clears hit target(s) velocity, also cancelling their ragdoll.
    :param can_kill: The hitbox can kill the hit target(s). If disabled, the target(s) cannot receive more damage than their current health.
    :param hit_ragdoll: The hitbox can hit ragdolls.
    :param hit_user: The hitbox can hit the user of the skill.
    :param single_target: The hitbox can only kill one target.
    :param branch: Proceed to a BRANCH on hit.
    :param branch_target: Force the hit target(s) to proceed to a BRANCH.
    :param branch_finisher: Proceed to a BRANCH if the hit was fatal.
    :param projectile_tag: The name of a projectile's tag. If matched with an existing projectile, the hitbox's origin is set to the projectile's position.
    :param link_user: Another player hitting this hitbox transfers the hit to the user instead.
    :param preview: Editor-only timeline range, ``[start, end]``. Not used at runtime.
    """
    if position is None:
        position = [0, 0, 4]
    if rotation is None:
        rotation = [0, 0, 0]
    if size is None:
        size = [6, 6, 6]
    node = {
        "K_NAME": "HITBOX",
        "POSITION": _vec3(position),
        "ROTATION": _vec3(rotation),
        "SIZE": _vec3(size),
        "STUN": stun,
        "STUN ANIM": stun_anim,
        "DAMAGE": damage,
        "DEBREE": debree,
        "ATTACK TYPE": attack_type,
        "BLOCKABLE": blockable,
        "360 BLOCK": blockable_360,
        "CANCEL ENEMY": cancel_enemy,
        "CLEAR KNOCKBACK": clear_knockback,
        "CAN KILL": can_kill,
        "HIT RAGDOLL": hit_ragdoll,
        "HIT USER": hit_user,
        "SINGLE TARGET": single_target,
        "BRANCH": branch,
        "BRANCH TARGET": branch_target,
        "BRANCH FINISHER": branch_finisher,
        "PROJECTILE TAG": projectile_tag,
        "IGNORE WAKEUP": ignore_wakeup,
        "LINK USER": link_user,
    }
    if preview is not None:
        node["PREVIEW"] = preview
    return node


def BRANCH(
    branch: str = "nil",
    random: str = "",
    last_hit: float = -1,
):
    """Proceed to a BRANCH on hit.

    :param branch: The BRANCH the user shall proceed to.
    :param random: Randomly selects a BRANCH to proceed to any time this NODE is activated. Branch names are seperated by commas.
    :param last_hit: Activates this NODE on a target hit in the last (value) seconds.
    """
    return {
        "K_NAME": "BRANCH",
        "BRANCH": branch,
        "RANDOM": random,
        "LAST HIT": last_hit,
    }


def VISUAL(
    effect: Effects = "Slash",
    amount: int = 1,
    texture: int = 0,
    color: str = "255, 255, 255",
    alt_color: str = "255, 255, 255",
    opacity: float = 0,
    alt_opacity: float = 0,
    position: list[float] | None = None,
    alt_position: list[float] | None = None,
    rotation: list[float] | None = None,
    alt_rotation: list[float] | None = None,
    size: float = 1,
    alt_size: float = 1,
    time: float | Literal["inf"] = 1,
    last_hit: float = -1,
    limb: BodyParts = "HumanoidRootPart",
    visual_tag: str = "nil",
    projectile_tag: str = "nil",
    run_on_server: bool = False,
    cancel_on_interrupt: bool = False,
    relative_from_branch: bool = False,
    can_collide: bool = False,
    easing_style: EasingStyles = "Linear",
    easing_direction: EasingDirections = "In",
):
    """Play a visual effect.

    :param effect: The effect to play. [no in-game documentation]
    :param amount: How many Effects to emit. If the selected Effect is "Mesh", the value of this property becomes the Mesh ID.
    :param texture: The effect's texture. Determined by an AssetID.
    :param color: The effect's color. (R, G, B)
    :param alt_color: The color to fade into over the course of the Effect's duration.
    :param opacity: The effect's transparency, with 0 being fully opaque and 1 being completely invisible.
    :param alt_opacity: The transparency to fade into.
    :param position: The effect's offset from the selected Limb. (X, Y, Z)
    :param alt_position: The offset to fade into.
    :param rotation: The effect's rotation. (X, Y, Z)
    :param alt_rotation: The rotation to fade into.
    :param size: Multiplier of the effect's size.
    :param alt_size: The size to fade into.
    :param time: How long the Effect should be active for. Alt (Property) use Time as the speed.
    :param last_hit: Activates this NODE on a target hit in the last (value) seconds.
    :param limb: The body part to play the effect on or use as the effect's center. [no in-game documentation]
    :param visual_tag: The name of the tag. Used by other VISUAL nodes to Cancel the effect, if the selected Effect is "Cancel"
    :param projectile_tag: The name of a projectile's tag. If matched with an existing projectile, the effect's origin (i.e. "Limb") is set to the projectile's position.
    :param run_on_server: Runs the effect serverside, recommended for weapons and such.
    :param cancel_on_interrupt: Cancels the effect when the skill is interrupted. Requires VISUAL TAG.
    :param relative_from_branch: Body part is selected from the Branch origin.
    :param can_collide: Enables collision on the effect, making it tangible.
    :param easing_style: The easing style of the effect. [no in-game documentation]
    :param easing_direction: The easing direction of the effect. [no in-game documentation]
    """
    if position is None:
        position = [0, 0, 0]
    if alt_position is None:
        alt_position = [0, 0, 0]
    if rotation is None:
        rotation = [0, 0, 0]
    if alt_rotation is None:
        alt_rotation = [0, 0, 0]
    return {
        "K_NAME": "VISUAL",
        "EFFECT": effect,
        "TIME": time,
        "POSITION": _vec3(position),
        "ROTATION": _vec3(rotation),
        "SIZE": size,
        "COLOR": color,
        "OPACITY": opacity,
        "ALT POSITION": _vec3(alt_position),
        "ALT ROTATION": _vec3(alt_rotation),
        "ALT SIZE": alt_size,
        "ALT COLOR": alt_color,
        "ALT OPACITY": alt_opacity,
        "TEXTURE": texture,
        "BODY PART": limb,
        "EASING STYLE": easing_style,
        "EASING DIRECTION": easing_direction,
        "PROJECTILE TAG": projectile_tag,
        "VISUAL TAG": visual_tag,
        "AMOUNT": amount,
        "RUN ON SERVER": run_on_server,
        "RELATIVE FROM BRANCH": relative_from_branch,
        "CANCEL ON INTERRUPT": cancel_on_interrupt,
        "CAN COLLIDE": can_collide,
        "LAST HIT": last_hit,
    }


def GRAB(
    limb: BodyParts = "HumanoidRootPart",
    target_limb: BodyParts = "HumanoidRootPart",
    position: list[float] | None = None,
    rotation: list[float] | None = None,
    time: float | Literal["inf"] = 1,
    last_hit: float = 1,
):
    """Grab a target's limb.

    :param limb: Which one of your limbs to use for grabbing.
    :param target_limb: Which one of the target's limbs to grab.
    :param position: The TARGET LIMB's offset from LIMB. (X, Y, Z)
    :param rotation: The TARGET LIMB's rotation. (X, Y, Z)
    :param time: How long the Grab should be active for.
    :param last_hit: Activates this NODE on a target hit in the last (value) seconds.
    """
    if position is None:
        position = [0, 0, 0]
    if rotation is None:
        rotation = [0, 0, 0]
    return {
        "K_NAME": "GRAB",
        "BODY PART": limb,
        "BODY PART2": target_limb,
        "TIME": time,
        "POSITION": _vec3(position),
        "ROTATION": _vec3(rotation),
        "LAST HIT": last_hit,
    }


def PROJECTILE(
    projectile_tag: str = "nil",
    position: list[float] | None = None,
    rotation: list[float] | None = None,
    size: list[float] | None = None,
    speed: float = 1,
    time: float | Literal["inf"] = 1,
    stun: float = 1,
    stun_anim: bool = False,
    ignore_wakeup: bool = True,
    damage: float = 1,
    debree: int = 0,
    attack_type: AttackType = "Melee",
    blockable: bool = True,
    blockable_360: bool = False,
    cancel_enemy: bool = True,
    clear_knockback: bool = False,
    can_kill: bool = True,
    hit_ragdoll: bool = False,
    hit_user: bool = False,
    single_target: bool = True,
    aim_last_hit: float = -1,
    continue_: bool = False,
    branch: str = "nil",
    branch_target: str = "nil",
    branch_collided: str = "nil",
    filter_interval: int = 1,
    reflect_count: int = 0,
    cache: bool = True,
):
    """Create a projectile.

    :param projectile_tag: The name of the tag. Used by VISUAL, HITBOX and SOUND nodes as a link to the projectile.
    :param position: The projectile's starting position, the origin being the player's center. (X, Y, Z)
    :param rotation: The projectile's rotation, relative to the player's rotation. (X, Y, Z)
    :param size: The size of the projectile. (X, Y, Z)
    :param speed: How fast the projectile should travel, in studs per second.
    :param time: How long the projectile should be active for. [no in-game documentation]
    :param stun: How long the stun on hit should last for, in seconds.
    :param stun_anim: Plays a generic stun animation on the hit target.
    :param ignore_wakeup: Ignore the wakeup stun immunity (disable for accurate M1s).
    :param damage: How much damage should be dealt on hit.
    :param debree: If not 0, causes destruction. The value determines the Debree Fidelity, which is 2 by default. Negative values don't spawn debree.
    :param attack_type: The attack type of the projectile. [no in-game documentation]
    :param blockable: The projectile is blockable from the front.
    :param blockable_360: The projectile is blockable regardless of orientation.
    :param cancel_enemy: Cancel the hit target(s).
    :param clear_knockback: Clears hit target(s) velocity, also cancelling their ragdoll.
    :param can_kill: The hitbox can kill the hit target(s). If disabled, the target(s) cannot receive more damage than their current health..
    :param hit_ragdoll: The hitbox can hit ragdolls.
    :param hit_user: The hitbox can hit the user of the skill.
    :param aim_last_hit: The projectile's rotation gets aligned towards the position of the LAST HIT target. (LAST HIT: target hit in the last (value) seconds.)
    :param continue_: The projectile continues travelling after hitting a target, or colliding with the environment.
    :param branch: Proceed to a BRANCH on hit.
    :param branch_target: Force the hit target(s) to proceed to a BRANCH.
    :param branch_collided: Proceed to a BRANCH if the projectile collided with the environment. If empty, the projectile ignores collisions
    :param filter_interval: The projectile, upon hitting a target, waits (value) seconds before it can hit the same target.
    :param reflect_count: How many times the projectile can bounce off the environment before despawning.
    :param cache: Stores projectile in the cache on hit, making PROJECTILE tag usable even after it's gone.
    """
    if position is None:
        position = [0, 0, 4]
    if rotation is None:
        rotation = [0, 0, 0]
    if size is None:
        size = [6, 6, 6]
    return {
        "K_NAME": "PROJECTILE",
        "DAMAGE": damage,
        "STUN": stun,
        "SPEED": speed,
        "SIZE": _vec3(size),
        "POSITION": _vec3(position),
        "ROTATION": _vec3(rotation),
        "ATTACK TYPE": attack_type,
        "PROJECTILE TAG": projectile_tag,
        "REFLECT COUNT": reflect_count,
        "FILTER INTERVAL": filter_interval,
        "BRANCH": branch,
        "BRANCH TARGET": branch_target,
        "BRANCH COLLIDED": branch_collided,
        "CONTINUE": continue_,
        "HIT RAGDOLL": hit_ragdoll,
        "STUN ANIM": stun_anim,
        "HIT USER": hit_user,
        "SINGLE TARGET": single_target,
        "BLOCKABLE": blockable,
        "360 BLOCK": blockable_360,
        "CAN KILL": can_kill,
        "AIM LAST HIT": aim_last_hit,
        "TIME": time,
        "IGNORE WAKEUP": ignore_wakeup,
        "DEBREE": debree,
        "CANCEL ENEMY": cancel_enemy,
        "CACHE": cache,
        "CLEAR KNOCKBACK": clear_knockback,
    }


def COUNTER(
    attack_type: list[AttackType] | None = None,
    time: float | Literal["inf"] = 1,
    stun: float = 1,
    cancel_enemy: bool = True,
    branch: str = "nil",
    branch_target: str = "nil",
    remove_on_hit: bool = True,
    reflect: bool = False,
    continue_: bool = False,
):
    """Start a counter.

    :param attack_type: The attack types to counter. [no in-game documentation]
    :param time: How long the counter is active for, in seconds.
    :param stun: How long the counter should stun the countered target for, in seconds.
    :param cancel_enemy: Cancels the countered target.
    :param branch: Proceed to a BRANCH upon successfully countering a target.
    :param branch_target: Force the countered target to proceed to a BRANCH.
    :param remove_on_hit: The counter gets removed upon activating.
    """
    if attack_type is None:
        attack_type = ["Melee"]
    return {
        "K_NAME": "COUNTER",
        "TIME": time,
        "STUN": stun,
        "ATTACK TYPE2": ",".join(attack_type),
        "BRANCH": branch,
        "BRANCH TARGET": branch_target,
        "CANCEL ENEMY": cancel_enemy,
        "REMOVE ON HIT": remove_on_hit,
        "REFLECT": reflect,
        "CONTINUE": continue_,
    }


def TAG(
    tag: str = "nil",
    value: str = "nil",
    time: float | Literal["inf"] = 1,
    check: bool = False,
    add_remove: bool = True,
    set_value: bool = True,
    branch: str = "nil",
    last_hit: float = -1,
):
    """Create a tag.

    :param tag: The name of the tag. This name can be used as a variable by all TAG nodes.
    :param value: Value of the tag. Can be a number, or a string of text.
    :param time: How long the tag should be active for, if changed.
    :param check: Checks if the tag's value matches (value). Performing *less than* and *greater than* operations can be done by prefixing the value with < or > (e.g. <1 for *less than 1*).
    :param add_remove: Only applicable if Set[_value] is false. If true, adds +(value) to the tag's value. If false, subtracts.
    :param set_value: Replaces the tag's value with (value)
    :param branch: Only applicable if Check is true. The branch that shall be proceeded to if Check successfully completes the comparison operation (e.g. if the tag's value is equal to (value), then proceed to BRANCH.)
    :param last_hit: Activates this NODE on a target hit in the last X seconds.
    """
    return {
        "K_NAME": "TAG",
        "TAG": tag,
        "VALUE": value,
        "TIME": time,
        "ADD/REMOVE": add_remove,
        "CHECK": check,
        "SET": set_value,
        "BRANCH": branch,
        "LAST HIT": last_hit,
    }


def STATE(
    state: States = "Stun",
    value: float = 1,
    time: float | Literal["inf"] = 1,
    cancel_on_end: bool = False,
    disable_burst: bool = False,
    last_hit: float = -1,
    check: bool = False,
    branch: str = "nil",
    state_tag: str = "nil",
):
    """Check or set a character state.

    :param state: The state to check or set. [no in-game documentation]
    :param value: Used for SpeedMultiplier, JumpMultiplier, and Scale.
    :param time: How long the State should be active for.
    :param cancel_on_end: The state gets cancelled when the skill ends.
    :param disable_burst: Burst is disabled while the State is active.
    :param last_hit: Activates this NODE on a target hit in the last X seconds.
    :param check: Checks if LAST HIT has that state
    :param branch: Only applicable if Check is true. The BRANCH that shall be proceeded to if Check successfully completes the state check, then proceed to BRANCH.
    """
    return {
        "K_NAME": "STATE",
        "STATE": state,
        "VALUE": value,
        "TIME": time,
        "DISABLE BURST": disable_burst,
        "CANCEL ON END": cancel_on_end,
        "LAST HIT": last_hit,
        "BRANCH": branch,
        "CHECK": check,
        "STATE TAG": state_tag,
    }


def TELEPORT(
    position: list[float] | None = None,
    rotation: list[float] | None = None,
    last_hit: float = -1,
    projectile_tag: str = "nil",
    relative_from_branch: bool = False,
    ignore_walls: bool = False,
):
    """Teleport to an offset.

    :param position: Character's offset from last hit. (X, Y, Z)
    :param rotation: Character's rotation at the location. (X, Y, Z)
    :param last_hit: Applies POSITION and ROTATION of the LAST HIT target
    :param projectile_tag: Prioritizes the projectile with this tag instead of the LAST HIT target.
    :param relative_from_branch: Prioritizes the origin of branch instead of the LAST HIT target
    """
    if position is None:
        position = [0, 0, 0]
    if rotation is None:
        rotation = [0, 0, 0]
    return {
        "K_NAME": "TELEPORT",
        "POSITION": _vec3(position),
        "ROTATION": _vec3(rotation),
        "PROJECTILE TAG": projectile_tag,
        "LAST HIT": last_hit,
        "RELATIVE FROM BRANCH": relative_from_branch,
        "IGNORE WALLS": ignore_walls,
    }


def ADD_AWAKENING(amount: float = 5):
    """Add to your awakening bar.

    :param amount: The amount to add to your awakening bar. [no in-game documentation]
    """
    return {"K_NAME": "ULTGIB", "AMOUNT": amount}


def ADD_HEALTH(amount: float = 5, can_kill: bool = False):
    """Add to your health bar.

    :param amount: The amount to add to your health bar.
    :param can_kill: Let the health lose be lethal. Off by default.
    """
    return {"K_NAME": "HPGIB", "AMOUNT": amount, "CAN KILL": can_kill}


def ADD_EVASION(amount: float = 5):
    """Add to your evasion bar.

    :param amount: The amount to add to your evasion bar. [no in-game documentation]
    """
    return {"K_NAME": "EVGIB", "AMOUNT": amount}


def HIT_CANCEL(
    time: float | Literal["inf"] = 1,
    flip: bool = False,
    endlag: float = 1,
    branch: str = "nil",
):
    """Cancel the skill.

    :param time: Proceeds to BRANCH depending on the value of Flip.
    :param flip: If set to FALSE: proceed to branch if a target WAS hit in the last (Time) seconds. If set to TRUE: proceed to branch if a target WASN'T hit in the last (Time) seconds.
    :param endlag: Become stunned for (value) seconds on cancel.
    :param branch: The BRANCH the user shall proceed to.
    """
    return {
        "K_NAME": "HITCNCL",
        "TIME": time,
        "ENDLAG": endlag,
        "BRANCH": branch,
        "FLIP": flip,
    }


def SET_COOLDOWN(key: int = -1, cooldown: float = -1):
    """Set the cooldown of a skill.

    :param key: The move to set cooldown for. (-1 for current move)
    :param cooldown: The cooldown itself. (-1 for default cooldown)
    """
    return {"KEY": key, "K_NAME": "SETCD", "COOLDOWN": cooldown}


def LOOP(loop_back: int = 1, loop_amount: int = 3, hold: bool = False):
    """Loop the current skill.

    :param loop_back: The number of nodes behind the LOOP node to loop. [no in-game documentation]
    :param loop_amount: The number of times to loop. [no in-game documentation]
    :param hold: Hold the skill state active. [no in-game documentation]
    """
    return {
        "LOOP BACK": loop_back,
        "HOLD": hold,
        "LOOP AMOUNT": loop_amount,
        "K_NAME": "LOOP",
    }


# --------------------------------------------------------------------------- #
# Nodes libjjs did not model. Field names come from the game's own block
# descriptions; the JSON keys below are confirmed against codes the game itself
# produced, and follow the same "setting name -> UPPER CASE" rule.
#
# Arguments default to ``None`` where the game's default is unknown, and are then
# omitted entirely, matching how the game serialises a node whose field was never
# touched.
# --------------------------------------------------------------------------- #
def PARTICLE(
    part_size: list[float] | str | None = None,
    texture: int | None = None,
    emit_count: int | None = None,
    rate: float | None = None,
    duration: float | None = None,
    color: str | None = None,
    size: str | None = None,
    brightness: float | None = None,
    projectile_tag: str | None = None,
    last_hit: float | None = None,
    **fields,
):
    """Emit particles.

    The arguments above are confirmed against a game-produced code. Every other
    setting from the block description is accepted through ``**fields`` verbatim
    (keys are the setting name in upper case)::

        TRANSPARENCY, SQUASH, LIFETIME, SPEED, ROTATION, ROT SPEED,
        ACCELERATION, DRAG, LIGHT EMISSION, LIGHT INFLUENCE, ZOFFSET,
        SPREAD ANGLE, POSITION, LOCK TO PART, BODY PART, ORIENTATION TYPE,
        EMISSION DIRECTION, FLIPBOOK SIZE, FLIPBOOK MODE, FLIPBOOK FRAMERATE,
        EMITTER SHAPE, EMITTER SHAPE INOUT, SHAPE PARTIAL, RUN ON SERVER,
        CLIENT SIDED, CANCEL TAG, CANCEL, CANCEL ON INTERRUPT

    :param part_size: Size of the emitted part; ``(0, 0, 0)`` emits from
        attachments instead.
    :param texture: Texture (asset) ID.
    :param emit_count: Particles spawned at once, used when ``duration`` is 0.
    :param rate: Particles per second, used when ``duration`` is above 0.
    :param duration: Seconds the emitter stays enabled.
    :param color: Colour sequence, ``"r,g,b r,g,b ..."``.
    :param size: Number sequence, ``"a, b, ..."``.
    :param brightness: How emissive the particle is.
    :param projectile_tag: Emit from a projectile with this tag.
    :param last_hit: Activate on a target hit in the last N seconds.
    """
    provided = {
        "PART SIZE": None if part_size is None else _vec3(part_size),
        "TEXTURE": texture,
        "EMIT COUNT": emit_count,
        "RATE": rate,
        "DURATION": duration,
        "COLOR": color,
        "SIZE": size,
        "BRIGHTNESS": brightness,
        "PROJECTILE TAG": projectile_tag,
        "LAST HIT": last_hit,
    }
    node = {"K_NAME": "PARTICLE"}
    node.update({k: v for k, v in provided.items() if v is not None})
    node.update(fields)
    return node


def LOOK(
    time: float | None = None,
    smoothness: float = 40,
    horizontal_only: bool | None = None,
    last_hit: float = -1,
    relative_from_branch: bool | None = None,
    projectile_tag: str | None = None,
    camera_direction: bool | None = None,
    grounded: bool | None = None,
):
    """Point the camera in a direction.

    :param time: How long the look action lasts.
    :param smoothness: Transition smoothness; lower is smoother. Defaults to 40.
    :param horizontal_only: Lock the camera to the horizontal axis.
    :param last_hit: Face a target hit in the last N seconds. Defaults to -1.
    :param relative_from_branch: Act relative to the branch that triggered this.
    :param projectile_tag: Look at the projectile with this tag.
    :param camera_direction: Look where the camera faces instead of the cursor.
    :param grounded: Affect root verticality based on the body.
    """
    provided = {
        "TIME": time,
        "HORIZONTAL ONLY": horizontal_only,
        "RELATIVE FROM BRANCH": relative_from_branch,
        "PROJECTILE TAG": projectile_tag,
        "CAMERA DIRECTION": camera_direction,
        "GROUNDED": grounded,
    }
    node = {"K_NAME": "LOOK", "SMOOTHNESS": smoothness, "LAST HIT": last_hit}
    node.update({k: v for k, v in provided.items() if v is not None})
    return node


def SETMELEE(combo: int | None = None, offset: float | None = None, last_hit: float = -1):
    """Force the user's melee count to a specific M1 for a while.

    :param combo: Which M1 to set; ``-1`` means the last M1 used, and ``0``
        prevents melee for ``offset`` seconds.
    :param offset: How long until the user's M1s reset.
    :param last_hit: Activate on a target hit in the last N seconds. Defaults to -1.
    """
    provided = {"COMBO": combo, "OFFSET": offset}
    node = {"K_NAME": "SETMELEE", "LAST HIT": last_hit}
    node.update({k: v for k, v in provided.items() if v is not None})
    return node


def raw(k_name: str, **fields) -> dict:
    """Build any node verbatim by its ``K_NAME``.

    An escape hatch for nodes with no dedicated builder::

        nodes.raw("PARTICLE", ID=1, TIME=2)
        nodes.raw("LOOK", **{"TARGET": "Head"})
    """
    return {"K_NAME": k_name, **fields}
