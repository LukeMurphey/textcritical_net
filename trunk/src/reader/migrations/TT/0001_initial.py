# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('name_slug', models.SlugField()),
                ('first_name', models.CharField(max_length=200, blank=True)),
                ('last_name', models.CharField(max_length=200, blank=True)),
                ('date_born', models.DateTimeField(null=True, verbose_name=b'date of birth', blank=True)),
                ('date_died', models.DateTimeField(null=True, verbose_name=b'date of death', blank=True)),
                ('description', models.TextField(blank=True)),
                ('meta_author', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Dialect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Division',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence_number', models.IntegerField()),
                ('title', models.CharField(max_length=200, null=True, blank=True)),
                ('title_slug', models.SlugField()),
                ('original_title', models.CharField(max_length=200, null=True, blank=True)),
                ('subtitle', models.CharField(max_length=200, blank=True)),
                ('descriptor', models.CharField(max_length=10, db_index=True)),
                ('type', models.CharField(max_length=50, null=True, blank=True)),
                ('level', models.IntegerField()),
                ('original_content', models.TextField(blank=True)),
                ('readable_unit', models.BooleanField(default=False, db_index=True)),
                ('parent_division', models.ForeignKey(blank=True, to='reader.Division', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Lemma',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lexical_form', models.CharField(max_length=200, db_index=True)),
                ('basic_lexical_form', models.CharField(max_length=200, db_index=True)),
                ('language', models.CharField(max_length=40)),
                ('reference_number', models.IntegerField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='RelatedWork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('related_levels', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Verse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sequence_number', models.IntegerField()),
                ('indicator', models.CharField(max_length=10)),
                ('content', models.TextField()),
                ('original_content', models.TextField()),
                ('division', models.ForeignKey(to='reader.Division')),
            ],
        ),
        migrations.CreateModel(
            name='WikiArticle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('search', models.CharField(unique=True, max_length=200, db_index=True)),
                ('article', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='WordDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('masculine', models.NullBooleanField(default=False)),
                ('feminine', models.NullBooleanField(default=False)),
                ('neuter', models.NullBooleanField(default=False)),
                ('geog_name', models.NullBooleanField(default=None)),
                ('numeral', models.NullBooleanField(default=None)),
                ('adverb', models.NullBooleanField(default=None)),
                ('infinitive', models.NullBooleanField(default=None)),
                ('participle', models.NullBooleanField(default=None)),
                ('voice', models.IntegerField(default=None, null=True, choices=[(b'', b''), (0, b'Active'), (1, b'Middle'), (2, b'Passive'), (3, b'Middle/Passive')])),
                ('mood', models.CharField(default=None, max_length=100, null=True)),
                ('tense', models.CharField(default=None, max_length=100, null=True)),
                ('person', models.IntegerField(default=None, null=True, choices=[(b'', b''), (1, b'First'), (2, b'Second'), (3, b'Third')])),
                ('number', models.IntegerField(default=None, null=True, choices=[(b'', b''), (0, b'Singular'), (1, b'Dual'), (2, b'Plural')])),
                ('part_of_speech', models.IntegerField(default=None, null=True, choices=[(b'', b''), (0, b'Noun'), (1, b'Verb'), (2, b'Adverb'), (3, b'Pronoun'), (4, b'Adjective'), (5, b'Preposition'), (6, b'Conjunction'), (7, b'Interjection')])),
                ('indeclinable', models.NullBooleanField(default=None)),
                ('particle', models.NullBooleanField(default=None)),
                ('superlative', models.IntegerField(default=None, null=True, choices=[(b'', b''), (0, b'Regular'), (1, b'Irregular')])),
                ('comparative', models.IntegerField(default=None, null=True, choices=[(b'', b''), (0, b'Regular'), (1, b'Irregular')])),
                ('expletive', models.NullBooleanField(default=None)),
                ('poetic', models.NullBooleanField(default=None)),
                ('clitic', models.IntegerField(default=None, null=True, choices=[(b'', b''), (0, b'Proclitic'), (1, b'Enclitic'), (2, b'Mesoclitic'), (3, b'Endoclitic')])),
                ('movable_nu', models.NullBooleanField(default=None)),
                ('description', models.CharField(default=b'', max_length=50, null=True)),
                ('meaning', models.CharField(default=b'', max_length=200, null=True)),
                ('cases', models.ManyToManyField(to='reader.Case')),
                ('dialects', models.ManyToManyField(to='reader.Dialect')),
                ('lemma', models.ForeignKey(to='reader.Lemma')),
            ],
        ),
        migrations.CreateModel(
            name='WordForm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('form', models.CharField(max_length=200, db_index=True)),
                ('basic_form', models.CharField(max_length=200, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('title_slug', models.SlugField(unique=True)),
                ('descriptor', models.CharField(max_length=30, blank=True)),
                ('copyright', models.CharField(max_length=200, blank=True)),
                ('date_written', models.DateTimeField(null=True, verbose_name=b'date written', blank=True)),
                ('language', models.CharField(max_length=200)),
                ('authors', models.ManyToManyField(to='reader.Author', blank=True)),
                ('editors', models.ManyToManyField(related_name='editors', to='reader.Author', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorkAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title_slug', models.SlugField(unique=True)),
                ('work', models.ForeignKey(to='reader.Work')),
            ],
        ),
        migrations.CreateModel(
            name='WorkSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.CharField(max_length=200)),
                ('resource', models.CharField(max_length=500)),
                ('description', models.TextField(blank=True)),
                ('work', models.ForeignKey(to='reader.Work')),
            ],
        ),
        migrations.CreateModel(
            name='WorkType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=40)),
            ],
        ),
        migrations.AddField(
            model_name='work',
            name='work_type',
            field=models.ForeignKey(blank=True, to='reader.WorkType', null=True),
        ),
        migrations.AddField(
            model_name='worddescription',
            name='word_form',
            field=models.ForeignKey(to='reader.WordForm'),
        ),
        migrations.AddField(
            model_name='relatedwork',
            name='related_work',
            field=models.ForeignKey(related_name='related_work', to='reader.Work'),
        ),
        migrations.AddField(
            model_name='relatedwork',
            name='work',
            field=models.ForeignKey(related_name='work', to='reader.Work'),
        ),
        migrations.AddField(
            model_name='division',
            name='work',
            field=models.ForeignKey(to='reader.Work'),
        ),
        migrations.AlterUniqueTogether(
            name='relatedwork',
            unique_together=set([('work', 'related_work')]),
        ),
    ]
