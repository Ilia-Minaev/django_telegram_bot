# Generated by Django 4.2.5 on 2023-09-07 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermodels',
            name='phone',
            field=models.PositiveIntegerField(blank=True, default=1, max_length=11, verbose_name='Номер телефона'),
            preserve_default=False,
        ),
    ]
