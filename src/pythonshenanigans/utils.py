def Branch(
    nodes: list[dict],
    conditions: list[dict] | None = None,
) -> dict:
    """Define a branch.

    :param nodes: The nodes in the branch.
    :param conditions: The conditions for the branch.
    """
    return {"nodes": nodes, "conditions": conditions or []}


def Properties(
    damage_multiplier: float = 1,
    knockback_multiplier: float = 1,
    invincible: bool = False,
    replace_skill_if_occupied: bool = False,
    prevent_override: bool = False,
    hide_in_awakening: bool = False,
    keep_when_moveset_switches: bool = False,
    hide_in_base: bool = False,
    use_when_obtained: bool = False,
    use_on_death: bool = False,
    no_stun: bool = False,
    no_cancel: bool = False,
    variant_tag: str = "-",
) -> dict:
    """Define the properties of a skill.

    :param damage_multiplier: The damage multiplier of the skill.
    :param knockback_multiplier: The knockback multiplier of the skill.
    :param invincible: Whether the skill makes you invincible.
    :param replace_skill_if_occupied: Prevent your custom moves from stacking.
    :param prevent_override: Whether the skill prevents override.
    :param hide_in_awakening: Whether the skill is hidden in the awakening moves.
    :param keep_when_moveset_switches: Whether the skill is kept when the player's moveset switches.
    :param hide_in_base: Whether the skill is hidden in the base moves.
    :param use_when_obtained: Whether the skill is used when the player gets it.
    :param use_on_death: Whether the skill is used when the player dies.
    :param no_stun: Whether the skill allows using other skills while active.
    :param no_cancel: Whether the skill ignores cancelling due to taking damage.
    :param variant_tag: The variant tag of the skill.
    """
    return {
        "DMG": damage_multiplier,
        "KNOCK": knockback_multiplier,
        "INV": invincible,
        "REP": replace_skill_if_occupied,
        "REP2": prevent_override,
        "AWK": hide_in_awakening,
        "KEEP": keep_when_moveset_switches,
        "AWK2": hide_in_base,
        "USE": use_when_obtained,
        "USEONDEATH": use_on_death,
        "NOSTUN": no_stun,
        "NOCANCEL": no_cancel,
        "VAR": variant_tag,
    }
