# Generated by Django 3.0.5 on 2020-05-03 12:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jokes', '0007_auto_20200502_1928'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='voted',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jokes.Player')),
                ('response', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jokes.Response')),
                ('session', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='jokes.Session')),
            ],
        ),
    ]
