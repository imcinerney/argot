# Generated by Django 2.1.2 on 2018-10-24 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Antonym',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='BaseWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExampleSentence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sentence', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='FormWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.BaseWord')),
            ],
        ),
        migrations.CreateModel(
            name='PartOfSpeech',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Synonym',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.FormWord')),
                ('synonym', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='synonym+', to='dictionary.FormWord')),
            ],
        ),
        migrations.CreateModel(
            name='VariantWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('base_word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.BaseWord')),
            ],
        ),
        migrations.CreateModel(
            name='WordDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('definition', models.CharField(max_length=300)),
                ('form_word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.FormWord')),
            ],
        ),
        migrations.AddField(
            model_name='formword',
            name='pos',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.PartOfSpeech'),
        ),
        migrations.AddField(
            model_name='examplesentence',
            name='definition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.WordDefinition'),
        ),
        migrations.AddField(
            model_name='antonym',
            name='antonym',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='antonym+', to='dictionary.FormWord'),
        ),
        migrations.AddField(
            model_name='antonym',
            name='base_word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.FormWord'),
        ),
    ]
