# -- code: utf-8 --
from __future__ import absolute_import

from django.db import models
from django.contrib.auth.models import User


class X509UserMapping(models.Model):
    """ 1:M mapping of Users to certificate (X.509) DNs (subjects) """

    user = models.ForeignKey(
        User,
        verbose_name="User",
        help_text="Django User associated with certificate.",
        default=None, blank=True, null=True,
        related_name="%(app_label)s_%(class)s_related",)

    cert_dn = models.CharField(
        help_text="Certificate matter to match on.",
        max_length=1024,
        blank=False,
        unique=True)

    required = models.BooleanField(
        help_text="This user must authenticate via x509.",
        default=False)

    def __str__(self):
        return "{0}:{1}".format(self.user.username, self.cert_dn)
