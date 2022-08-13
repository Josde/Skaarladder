tierWeights = {
    "UNRANKED": 0,
    "IRON": 0,
    "BRONZE": 1,
    "SILVER": 2,
    "GOLD": 3,
    "PLATINUM": 4,
    "DIAMOND": 5,
    "MASTER": 6,
    "GRANDMASTER": 6,
    "CHALLENGER": 6,
}

rankWeights = {
    "IV": 0,
    "III": 1,
    "II": 2,
    "I": 3,
    "NONE": 0,
}

riotToOPGGRegions = {
    "BR1": "BR",
    "EUN1": "EUNE",
    "EUW1": "EUW",
    "NA1": "NA",
    "JP1": "JP",
    "KR": "www",  # instead of kr.op.gg its www.op.gg
    "LA1": "LAN",
    "LA2": "LAS",
    "OC1": "OCE",
    "RU": "RU",
    "TR1": "TR",
}

# Form choices

platformChoices = [
    ("euw1", "EUW"),
    ("na1", "NA"),
    ("br1", "BR"),
    ("eun1", "EUNE"),
    ("jp1", "JP"),
    ("kr", "KR"),
    ("la1", "LAN"),
    ("la2", "LAS"),
    ("oc1", "OCE"),
    ("ru", "RU"),
    ("tr1", "TR"),
]

regionChoices = [
    ("europe", "europe"),
    ("americas", "americas"),
    ("asia", "asia"),
]

tierChoices = [
    ("UNRANKED", "UNRANKED"),
    ("IRON", "IRON"),
    ("BRONZE", "BRONZE"),
    ("SILVER", "SILVER"),
    ("GOLD", "GOLD"),
    ("PLATINUM", "PLATINUM"),
    ("DIAMOND", "DIAMOND"),
    ("MASTER", "MASTER"),
    ("GRANDMASTER", "GRANDMASTER"),
    ("CHALLENGER", "CHALLENGER"),
]
rankChoices = [("I", "I"), ("II", "II"), ("III", "III"), ("IV", "IV"), ("NONE", "NONE")]

# Settings

UPDATE_DELAY = 1800


# HTML Attrs

red_text_style = "color:rgb(249,36,114);"
green_text_style = "color:rgb(180, 210, 115);"
default_form_style = "bg-neutral-900 text-white m-4 invalid:border-pink-500 invalid:text-pink-600"
