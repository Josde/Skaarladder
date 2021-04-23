def rankToLP(rank, tier, points):
    rankWeights = {
        "IRON" : 0,
        "BRONZE" : 1,
        "SILVER" : 2,
        "GOLD" : 3,
        "PLATINUM" : 4,
        "DIAMOND" : 5
    }
    tierWeights = {
        "IV" : 0,
        "III" : 1,
        "II" : 2,
        "I" : 3
    }
    return (rankWeights[rank]) * 400 + (tierWeights[tier]) * 100 + int(points)