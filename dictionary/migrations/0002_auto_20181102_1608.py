# Generated by Django 2.1.2 on 2018-11-02 20:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='antonym',
            name='antonym',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.BaseWord'),
        ),
        migrations.AlterField(
            model_name='synonym',
            name='synonym',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.BaseWord'),
        ),
    ]