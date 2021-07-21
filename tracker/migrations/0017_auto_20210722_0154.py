# Generated by Django 3.2 on 2021-07-21 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0016_alter_challenge_lastupdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenge',
            name='queueType',
            field=models.CharField(choices=[('RANKED_SOLO_5x5', 'SoloQ'), ('RANKED_FLEX_5x5', 'Flex')], default='RANKED_SOLO_5x5', max_length=25),
        ),
        migrations.AlterField(
            model_name='trackedplayers',
            name='region',
            field=models.CharField(choices=[('EUW1', 'EUW'), ('BR1', 'BR'), ('EUN1', 'EUNE'), ('JP1', 'JP'), ('KR1', 'KR'), ('LA1', 'LAN'), ('LA2', 'LAS'), ('OC1', 'OCE'), ('RU', 'RU'), ('TR1', 'TR')], default='EUW', max_length=10),
        ),
    ]