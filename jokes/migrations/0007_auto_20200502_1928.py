# Generated by Django 3.0.5 on 2020-05-02 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jokes', '0006_session_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='status',
            field=models.CharField(default='start', max_length=80),
        ),
    ]
