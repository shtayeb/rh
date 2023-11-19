# Generated by Django 4.0.6 on 2023-11-14 04:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("rh", "0004_alter_project_implementing_partners_and_more"),
        ("stock", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="stocktype",
            name="cluster",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="rh.cluster"
            ),
        ),
    ]
