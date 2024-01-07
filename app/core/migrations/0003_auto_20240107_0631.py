# Generated by Django 3.2.23 on 2024-01-07 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_recipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='price',
            field=models.DecimalField(decimal_places=2, default=5.5, max_digits=5),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='time_minutes',
            field=models.IntegerField(),
        ),
    ]
