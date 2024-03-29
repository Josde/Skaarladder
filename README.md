![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
![Heroku](https://img.shields.io/badge/heroku-%23430098.svg?style=for-the-badge&logo=heroku&logoColor=white)

# Skaarladder
Skaarladder is an open-source ladder creation web app for League of Legends. It allows you to create ladders and compete with your friends to see who can climb higher on SoloQ.

![image](https://github.com/Josde/Skaarladder/assets/3825181/96dc807e-47ba-4a89-bfd4-fc2e4f35d0a2)
![image](https://github.com/Josde/Skaarladder/assets/3825181/89812878-62d1-493e-9a16-bb39b302fa89)

## Deploying basics
Modify ALLOWED_HOSTS in settings.py to your domain of choice.  
Configure the following config vars or put them in a .env file in the project root:
  - API_KEY: Your Riot Games API Key.
  - SECRET_KEY: Your Django secret key.  
  - REDIS: Set to any value
    - REDIS_HOST: The IP of your redis DB
    - REDIS_PORT: Port of your redis DB
    - REDIS_DB: Database that will store queue data
    - REDIS_PASSWORD: Your redis password
  Optionally configure:
  - HEROKU: Set to any value if you are deploying on Heroku
  - SENTRY: Set to any value if you want to use Sentry
    - SENTRY_DSN: Your sentry URL
    - RQ_SENTRY_DSN: Optional unless you want to use a different Sentry endpoint. Used only for RQ jobs. (default: same as SENTRY_DSN)
  - UPDATE_DELAY: The delay between updates, in minutes (default: 10)
  - PLAYER_DATA_UPDATE_DELAY: The delay between checks for player name changes, region changes, etc. (default: 360, meaning 6 hours)
  - RELEASE_CHECK: Set to any value if you want to check for releases. If releases are found, you will be notified through Sentry and the console.
  - RELEASE_CHECK_DELAY = The delay between update checks, in minutes (default: 1440, meaning 1 day)

# Deploying through Heroku
After completing the previous step, go into Heroku bash and run:  
  - python manage.py migrate --run-syncdb
  - python manage.py createsuperuser  
Afterwards, just restart the dyno and add a worker if needed to execute the procfile.
## Deploying locally
After completing the general setup, do the following:
  - Start your Redis server, which must have been configured through environment variables previously.
  - Go to the project root and activate a venv.  
  - Run python -m pip install -r requirements.txt
  - Set-up your database in settings.py
  - Run `python manage.py migrate --run-syncdb`
  - Run `python manage.py rqworker high default --with-scheduler`
    - If you are running on Windows, you have to execute the previous command in WSL. 
  - Run the application through your server of choice. Using Gunicorn as an example, run `gunicorn SoloQTracker.wsgi:application`
## Demo
You can check out a demo of this running at http://skaarl.josde.me/
