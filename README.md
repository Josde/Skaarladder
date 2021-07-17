# SimpleSoloQTracker
Very simple and WIP SoloQ Challenge tracker app for Heroku. 

## Deploying through heroku
Deploy this repo through a Heroku dyno. 
Configure the following config vars:
  - API_KEY: Your Riot Games API Key.
  - SECRET_KEY: Your Django secret key.  

Then, go into Heroku bash and run:  
  - python manage.py migrate --run-syncdb
  - python manage.py createsuperuser


Optionally, you may configure these config vars. If you don't, you can always add more players through your Django admin panel: 
  - PLAYERS: Comma-separated player list. Example: player1, player2...
  - STARTING_RANKS: Comma-separated starting ranks, in "RANK TIER POINT" format. Example: BRONZE II 20,SILVER IV 100,GOLD I 0
  - IGNORED_PLAYERS: Players that are still in the database, but get ignored. Currently only configurable through this variable!
  - QUEUE_TYPE: Either RANKED_SOLO_5x5 or RANKED_FLEX_5x5. If not configured, defaults to RANKED_SOLO_5x5.
  - ENDDATE_YEAR, ENDDATE_MONTH, ENDDATE_DAY: The end date for your challenge. If not set, will default to ending in a month.  
  - REGION: The default API region of your players (EUW1, EUN1, KR...). If not set, will default to EUW1.  
## Deploying locally
Clone the repo.  
Create a PostGreSQL database called "soloqtracker" and give all permissions to a user.  
Configure your config vars in KEY=VALUE format and save as ".env" in the repo root folder.  
When deploying locally, you will also need to configure the following config vars:  
  - DATABASE_USER: Your PostGreSQL user for the app database.  
  - DATABASE_PASSWORD: Your user's password. 

Then, go into the project's folder and run:  
  - python manage.py migrate --run-syncdb
  - python manage.py createsuperuser  

Finally, run "gunicorn SimpleSoloQTracker.wsgi:application". Your SoloQ tracker is now running!
## Demo
You can check out a demo of this running at http://soloq.josde.me/
