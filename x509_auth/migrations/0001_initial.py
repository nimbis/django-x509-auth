# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='X509UserMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cert_dn', models.CharField(help_text=b'Certificate matter to match on.', unique=True, max_length=1024)),
                ('user', models.ForeignKey(related_name=b'x509_auth_x509usermapping_related', default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'Django User associated with certificate.', null=True, verbose_name=b'User')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
