# Generated by Django 4.0.5 on 2022-07-29 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0005_alter_player_platform_alter_player_region'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='ignore_unranked',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='challenge_player',
            name='starting_rank',
            field=models.CharField(choices=[('I', 'I'), ('II', 'II'), ('III', 'III'), ('IV', 'IV'), ('NONE', 'NONE')], max_length=20),
        ),
        migrations.AlterField(
            model_name='challenge_player',
            name='starting_tier',
            field=models.CharField(choices=[('UNRANKED', 'UNRANKED'), ('IRON', 'IRON'), ('BRONZE', 'BRONZE'), ('SILVER', 'SILVER'), ('GOLD', 'GOLD'), ('PLATINUM', 'PLATINUM'), ('DIAMOND', 'DIAMOND'), ('MASTER', 'MASTER'), ('GRANDMASTER', 'GRANDMASTER'), ('CHALLENGER', 'CHALLENGER')], max_length=30),
        ),
        migrations.AlterField(
            model_name='player',
            name='rank',
            field=models.CharField(choices=[('I', 'I'), ('II', 'II'), ('III', 'III'), ('IV', 'IV'), ('NONE', 'NONE')], default='NONE', max_length=5),
        ),
        migrations.AlterField(
            model_name='player',
            name='tier',
            field=models.CharField(choices=[('UNRANKED', 'UNRANKED'), ('IRON', 'IRON'), ('BRONZE', 'BRONZE'), ('SILVER', 'SILVER'), ('GOLD', 'GOLD'), ('PLATINUM', 'PLATINUM'), ('DIAMOND', 'DIAMOND'), ('MASTER', 'MASTER'), ('GRANDMASTER', 'GRANDMASTER'), ('CHALLENGER', 'CHALLENGER')], default='UNRANKED', max_length=100),
        ),
    ]
