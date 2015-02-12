# -- code: utf-8 --
from __future__ import absolute_import

from django.contrib.auth.backends import ModelBackend

from .models import UserCertMapping


class AuthenticationBackend(ModelBackend):

    def authenticate(self, **credentials):
        '''
        Try to look up User in UserCertMaps, returning None if not found
        '''

        if 'dn' not in credentials or 'verified' not in credentials:
            return None

        if not credentials['verified'] == 'SUCCESS':
            return None

        try:
            return UserCertMapping.objects.get(cert_dn=credentials['dn']).user
        except UserCertMapping.DoesNotExist:
            return None
