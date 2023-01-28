import tracker.utils.constants as constants


def rank_to_lp(tier: str, rank: str, points: int) -> int:
    """Turns the rank and tier of a player into a LP number.
    Args:
        tier (str): Rank is IRON, BRONZE... and so on.
        rank (str): Tier is IV, III... and so on
        points (str): LPs

    Raises:
        TypeError: Raised if points is not the decimal representation of a number.
        ValueError: Raised if rank or tier are not found.

    Returns:
        int: The full amount of LPs that it would take to get from IRON IV 0LP to the input.
            Please note that this ignores promos, since they don't affect LP.
    """
    sanitized_rank = rank.upper().strip()
    sanitized_tier = tier.upper().strip()
    # If error, we return 0LP silently.
    if (sanitized_rank not in constants.RANK_WEIGHTS.keys()) or (sanitized_tier not in constants.TIER_WEIGHTS.keys()):
        return 0
    if tier in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
        lp = (constants.TIER_WEIGHTS[sanitized_tier]) * 400 + int(points)
    else:
        lp = (constants.TIER_WEIGHTS[sanitized_tier]) * 400 + (constants.RANK_WEIGHTS[sanitized_rank]) * 100 + int(points)
    return lp

