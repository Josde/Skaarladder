from decouple import config

# League of Legends

TIER_WEIGHTS = {
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

RANK_WEIGHTS = {
    "IV": 0,
    "III": 1,
    "II": 2,
    "I": 3,
    "NONE": 0,
}

# Maps riot platform names to OPGG URL
RIOT_TO_OPGG_REGIONS = {
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

PLATFORM_CHOICES = [
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

REGION_CHOICES = [
    ("europe", "europe"),
    ("americas", "americas"),
    ("asia", "asia"),
]

TIER_CHOICES = [
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
RANK_CHOICES = [("I", "I"), ("II", "II"), ("III", "III"), ("IV", "IV"), ("NONE", "NONE")]

# Settings
# Delays are in minutes

UPDATE_DELAY = int(config("UPDATE_DELAY", 10))
PLAYER_DATA_UPDATE_DELAY = int(
    config("PLAYER_DATA_UPDATE_DELAY", 360)
)  # Time between updates of user data (name, avatar...)
RELEASE_CHECK = bool(config("RELEASE_CHECK", True))
RELEASE_CHECK_DELAY = int(config("RELEASE_CHECK_DELAY", 1440))
MAX_STREAK_LENGTH = 10  # Maximum number of matches that will be queried when checking for winstreaks. Making this higher will make hitting a ratelimit easier.
# Obviously, change these two constants if you are forking the repo to make your own.

RELEASE_USER = "Josde"  # User that uploaded this to github.
RELEASE_REPO = "Skaarladder"  # Name of the repo
RELEASE_VERSION = "1.0-rc"
# HTML Attrs

RED_TEXT_STYLE = "color:rgb(249,36,114);"
GREEN_TEXT_STYLE = "color:rgb(180, 210, 115);"
DEFAULT_FORM_STYLE = "bg-neutral-900 text-white m-4 invalid:border-pink-500 "
DEFAULT_CONTAINER_STYLE = "block whitespace-nowrap"
