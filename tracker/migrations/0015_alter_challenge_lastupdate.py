# Generated by Django 3.2 on 2021-07-21 22:25

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0014_alter_challenge_lastupdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenge',
            name='lastUpdate',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 21, 22, 25, 44, 888557, tzinfo=utc)),
        ),
    ]