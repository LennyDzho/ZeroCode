# Generated by Django 5.2.1 on 2025-05-12 21:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dialogs', '0003_message'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dialog',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dialogs', to='projects.project'),
        ),
    ]
