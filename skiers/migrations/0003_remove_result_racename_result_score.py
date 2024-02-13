# Generated by Django 5.0.2 on 2024-02-10 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skiers', '0002_racer_result'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='result',
            name='racename',
        ),
        migrations.AddField(
            model_name='result',
            name='score',
            field=models.FloatField(default=3),
            preserve_default=False,
        ),
    ]
