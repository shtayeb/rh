# Generated by Django 4.0.10 on 2023-06-15 06:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='targetlocation',
            name='activity_plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.activityplan'),
        ),
    ]