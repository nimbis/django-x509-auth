# -- code: utf-8 --
from __future__ import absolute_import

from django.contrib.auth.backends import ModelBackend

from .models import X509UserMapping


class AuthenticationBackend(ModelBackend):

    def authenticate(self, **credentials):
        """
        Try to look up User in X509UserMaps, returning None if not found
        """

        if 'dn' not in credentials or 'verified' not in credentials:
            return None

        if not credentials['verified'] == 'SUCCESS':
            return None

        try:
            return X509UserMapping.objects.get(cert_dn=credentials['dn']).user
        except X509UserMapping.DoesNotExist:
            return None
