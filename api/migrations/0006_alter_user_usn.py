# Generated by Django 4.1.11 on 2024-04-01 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_user_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='usn',
            field=models.CharField(max_length=12, primary_key=True, serialize=False, unique=True),
        ),
    ]
