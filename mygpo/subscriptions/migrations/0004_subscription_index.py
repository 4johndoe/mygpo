# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0003_remove_podcastconfig'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='subscription',
            index_together=set([('podcast', 'user'), ('user', 'client')]),
        ),
    ]
