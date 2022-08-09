![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)

# SimpleSoloQTracker
Skaarladder is an open-source ladder creation web app for League of Legends. It allows you to create ladders and compete with your friends to see who can climb higher on SoloQ.

## Deploying through heroku
Deploy this repo through a Heroku dyno. 
Configure the following config vars:
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

Then, go into Heroku bash and run:  
  - python manage.py migrate --run-syncdb
  - python manage.py createsuperuser

## Deploying locally
coming soon!
## Demo
You can check out a demo of this running at http://soloq.josde.me/
