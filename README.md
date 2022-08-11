![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)

# SimpleSoloQTracker
Skaarladder is an open-source ladder creation web app for League of Legends. It allows you to create ladders and compete with your friends to see who can climb higher on SoloQ.

## Deploying basics
Configure the following config vars or put them in a .env file in the project root:
  - API_KEY: Your Riot Games API Key.
  - SECRET_KEY: Your Django secret key.  
  - REDIS: whatever value
    - REDIS_HOST: The IP of your redis DB
    - REDIS_PORT: Port of your redis DB
    - REDIS_DB: Database that will store queue data
    - REDIS_PASSWORD: Your redis password
  Optionally configure:
  - HEROKU: With whatever value, if you are deploying on Heroku
  - SENTRY: With whatever value, if you are using Sentry
    - SENTRY_DSN: Your sentry URL

# Deploying through Heroku
After completing the previous step, go into Heroku bash and run:  
  - python manage.py migrate --run-syncdb
  - python manage.py createsuperuser  
Afterwards, just restart the dyno and add workers if needed to execute the procfile.
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
You can check out a demo of this running at http://soloq.josde.me/
