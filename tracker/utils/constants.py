from decouple import config

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
# Delays are in minutes

UPDATE_DELAY = int(config("UPDATE_DELAY", 10))
RELEASE_CHECK = bool(config("RELEASE_CHECK", True))
RELEASE_CHECK_DELAY = int(config("RELEASE_CHECK_DELAY", 3600))
RELEASE_USER = config("RELEASE_USER", "Josde")  # User that uploaded this to github
RELEASE_REPO = config("RELEASE_REPO", "Skaarladder")  # Name of the repo

# HTML Attrs

red_text_style = "color:rgb(249,36,114);"
green_text_style = "color:rgb(180, 210, 115);"
default_form_style = "bg-neutral-900 text-white m-4 invalid:border-pink-500 invalid:text-pink-600"
