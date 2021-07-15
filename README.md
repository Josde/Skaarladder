# SimpleSoloQTracker
Very simple and WIP SoloQ Challenge tracker app for Heroku. 

## Deploying through heroku
Deploy this repo through a Heroku dyno. Configure the following config vars:
  - API_KEY: Your Riot Games API Key.
  - SECRET_KEY: Your Django secret key.
  - ENDDATE_YEAR, ENDDATE_MONTH, ENDDATE_DAY: The end date for your challenge
  - REGION: The default region of your players. For example: euw1. If you don't set this, you can always modify the database manually, but it's a chore.
Optionally, you may configure these config vars. If you don't, you can always add more players through your Django admin panel: 
  - PLAYERS: Comma-separated player list. Example: player1, player2...
  - STARTING_RANKS: Comma-separated starting ranks, in "RANK TIER POINT" format. Example: BRONZE II 20,SILVER IV 100,GOLD I 0
  - IGNORED_PLAYERS: Players that are still in the database, but get ignored. Currently only configurable through this variable!
  - QUEUE_TYPE: Either RANKED_SOLO_5x5 or RANKED_FLEX_5x5. If not configured, defaults to RANKED_SOLO_5x5.
## Deploying locally
Clone the repo, configure the config vars in KEY=VALUE format and save as ".env" in the repo root folder. 
Then, run "gunicorn SimpleSoloQTracker.wsgi:application"
## Demo
You can check out a demo of this running at http://soloq.josde.me/
