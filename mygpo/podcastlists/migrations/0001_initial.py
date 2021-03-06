# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PodcastList',
            fields=[
                ('id', uuidfield.fields.UUIDField(max_length=32, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=512)),
                ('slug', models.SlugField(max_length=128)),
                ('created', models.DateTimeField()),
                ('modified', models.DateTimeField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PodcastListEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.PositiveSmallIntegerField()),
                ('object_id', uuidfield.fields.UUIDField(max_length=32)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=django.db.models.deletion.PROTECT)),
                ('podcastlist', models.ForeignKey(related_name=b'entries', to='podcastlists.PodcastList')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='podcastlistentry',
            unique_together=set([('podcastlist', 'order'), ('podcastlist', 'content_type', 'object_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='podcastlist',
            unique_together=set([('user', 'slug')]),
        ),
    ]
