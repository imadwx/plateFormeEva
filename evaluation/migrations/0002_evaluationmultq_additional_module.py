# Generated by Django 5.0.6 on 2024-06-30 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluationmultq',
            name='additional_module',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]