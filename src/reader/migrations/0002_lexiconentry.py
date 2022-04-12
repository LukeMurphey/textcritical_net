# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from operator import mod

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LexiconEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lemma', models.ForeignKey(to='reader.Lemma', on_delete=models.SET_NULL)),
                ('verse', models.ForeignKey(to='reader.Verse', on_delete=models.CASCADE)),
                ('work', models.ForeignKey(to='reader.Work', on_delete=models.CASCADE)),
            ],
        ),
    ]
