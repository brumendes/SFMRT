# Generated by Django 2.1.2 on 2018-11-21 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QA', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='energia',
            name='slug',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Designação'),
        ),
    ]
