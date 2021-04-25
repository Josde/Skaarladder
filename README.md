# SimpleSoloQTracker
Very simple and WIP SoloQ Challenge tracker app for Heroku. 

## Deploying through heroku
Deploy this repo through a Heroku dyno. Configure the following config vars:
  - API_KEY: Your Riot Games API Key.
  - PLAYERS: Comma-separated player list. Example: player1, player2...
  - STARTING_RANKS: Comma-separated starting ranks, in "RANK TIER POINT" format. Example: BRONZE II 20,SILVER IV 100,GOLD I 0
  - REGION: The region of your players. Example: euw1
## Deploying locally
Clone the repo, configure the config vars in KEY=VALUE format and save as ".env" in the repo root folder. 
Then, run "gunicorn SimpleSoloQTracker.wsgi:application"
## Demo
You can check out a demo of this running at http://soloq.josde.me/
