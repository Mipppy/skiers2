# Generated by Django 5.0.2 on 2024-02-11 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skiers', '0003_remove_result_racename_result_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='sites',
            name='title',
            field=models.CharField(default='placeholder', max_length=255),
            preserve_default=False,
        ),
    ]
