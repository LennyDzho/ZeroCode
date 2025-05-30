# Generated by Django 5.2.1 on 2025-05-12 18:05

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('models_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dialog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(default='Новый диалог', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('model', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='models_app.model')),
            ],
        ),
    ]
