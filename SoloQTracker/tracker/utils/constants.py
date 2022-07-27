tierWeights = {
    "IRON": 0,
    "BRONZE": 1,
    "SILVER": 2,
    "GOLD": 3,
    "PLATINUM": 4,
    "DIAMOND": 5
}

rankWeights = {
    "IV": 0,
    "III": 1,
    "II": 2,
    "I": 3
}

riotToOPGGRegions = {
    "BR1": "BR",
    "EUN1": "EUNE",
    "EUW1": "EUW",
    "JP1": "JP",
    "KR": "www",  #instead of kr.op.gg its www.op.gg
    "LA1": "LAN",
    "LA2": "LAS",
    "OC1": "OCE",
    "RU": "RU",
    "TR1": "TR"
}

# Form choices 

platformChoices = [('euw1', 'euw1'),
                     ("br1","br1"),
                     ("eun1", "eun1"),
                     ('jp1', 'jp1'),
                     ('kr1', 'kr1'),
                     ('la1', 'la1'),
                     ('la2', 'la2'),
                     ('oc1', 'oc1'),
                     ('ru', 'ru'),
                     ('tr1', 'tr1')]

regionChoices = [('europe', 'europe'),
                     ("americas","americas"),
                     ("asia", "asia"),
                     ]

tierChoices = [('IRON', 'IRON'),
                ('BRONZE', 'BRONZE'),
                ('SILVER', 'SILVER'),
                ('GOLD', 'GOLD'),
                ('PLATINUM', 'PLATINUM'),
                ('DIAMOND', 'DIAMOND'),
                ('MASTER_PLUS', 'MASTER_PLUS')]
rankChoices = [('I', 'I'),
                ('II', 'II'),
                ('III', 'III'),
                ('IV', 'IV')]

# Settings

UPDATE_DELAY = 600