# Generated by Django 3.2 on 2021-08-11 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0019_auto_20210722_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaguedata',
            name='puuid',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='trackedplayers',
            name='puuid',
            field=models.CharField(default='', max_length=100),
        ),
    ]