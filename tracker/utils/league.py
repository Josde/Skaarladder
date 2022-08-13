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
    if (rank not in constants.rankWeights) or (tier not in constants.tierWeights):
        return 0
    if tier in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
        return (constants.tierWeights[tier.upper()]) * 400 + int(points)
    else:
        return (constants.tierWeights[tier.upper()]) * 400 + (constants.rankWeights[rank.upper()]) * 100 + int(points)
