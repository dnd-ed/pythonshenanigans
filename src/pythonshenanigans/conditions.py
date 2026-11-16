def IN_AIR(flip: bool = False) -> dict:
    """Check if the player is in the air.

    :param flip: If false, the player must be in the air. If true, the player must not be in the air.
    """
    return {"K_NAME": "AIR", "FLIP": flip}


def IS_JUMPING(flip: bool = False) -> dict:
    """Check if the player is jumping.

    :param flip: If false, the player must be jumping. If true, the player must not be jumping.
    """
    return {"K_NAME": "JUMP", "FLIP": flip}


def HAS_TARGET(flip: bool = False) -> dict:
    """Check if the player is hovering their cursor over another player.

    :param flip: If false, the player must be hovering their cursor over another player. If true, the player must not be hovering their cursor over another player.
    """
    return {"K_NAME": "AIM", "FLIP": flip}


def IS_AWAKENED(flip: bool = False) -> dict:
    """Check if the player has their awakening.

    :param flip: If false, the player must have their awakening. If true, the player must not have their awakening.
    """
    return {"K_NAME": "ULT", "FLIP": flip}


def HAS_AWK_BAR(amount: float = 2, flip: bool = False) -> dict:
    """Check how much of the awakening bar the player has.

    :param amount: The amount of the awakening bar to check.
    :param flip: If false, the player must have (amount) of awakening or more. If true, the player must have less than (amount) of awakening.
    """
    return {"K_NAME": "BAR", "AMOUNT": amount, "FLIP": flip}


def DURABILITY(durability: float = 1) -> dict:
    """Check how much durability the current move has.

    :param durability: The durability of the current move to check. (may be inacurate, please change if so)
    """
    return {"K_NAME": "DUR", "DURABILITY": durability}


def HAS_HEALTH(amount: float = 1, flip: bool = False) -> dict:
    """Check how much health the player has. (may be inacurate, please change if so)

    :param amount: The amount of health to check.
    :param flip: If false, the player must have (amount) of health or more. If true, the player must have less than (amount) of health.
    """
    return {"K_NAME": "HP", "AMOUNT": amount, "FLIP": flip}


def IS_IN_DOMAIN(flip: bool = False) -> dict:
    """Check if the player is in a domain.

    :param flip: If false, the player must be in a domain. If true, the player must not be in a domain.
    """
    return {"K_NAME": "DOMAIN", "FLIP": flip}


def IS_HOLDING(flip: bool = False) -> dict:
    """Check if the player is holding the skill key.

    :param flip: If false, the player must be holding the skill key. If true, the player must not be holding the skill key.
    """
    return {"K_NAME": "HOLD", "FLIP": flip}
