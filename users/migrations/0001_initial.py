# Generated by Django 4.0.6 on 2023-04-12 18:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rh', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('phone', models.CharField(blank=True, max_length=200, null=True)),
                ('whatsapp', models.CharField(blank=True, max_length=200, null=True)),
                ('position', models.CharField(blank=True, max_length=200, null=True)),
                ('skype', models.CharField(blank=True, max_length=200, null=True)),
                ('old_id', models.CharField(blank=True, max_length=200, null=True)),
                ('is_cluster_contact', models.BooleanField(default=False)),
                ('visits', models.IntegerField(blank=True, null=True)),
                ('clusters', models.ManyToManyField(to='rh.cluster')),
                ('country', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.location')),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.organization')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
