# Generated by Django 2.1.2 on 2018-11-21 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QA', '0003_auto_20181121_1625'),
    ]

    operations = [
        migrations.AlterField(
            model_name='energia',
            name='slug',
            field=models.SlugField(max_length=20, unique=True, verbose_name='Designação'),
        ),
    ]