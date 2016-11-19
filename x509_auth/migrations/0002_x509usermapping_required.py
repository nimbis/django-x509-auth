# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('x509_auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='x509usermapping',
            name='required',
            field=models.BooleanField(default=False, help_text=b'This user must authenticate via x509.'),
        ),
    ]
