# -- code: utf-8 --
from __future__ import absolute_import

from functools import wraps

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import available_attrs
from django.core.urlresolvers import reverse_lazy

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


def is_X509_authed(user):
    """
    Check how this user authenticated (did they use our backend?)
    """

    return (hasattr(user, 'backend') and
            user.backend == 'x509_auth.auth_backend.AuthenticationBackend')

def X509_required(view_func):
    return user_passes_test(is_X509_authed,
                            login_url=reverse_lazy('auth'))(view_func)

def X509_required2(view_func):

    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view
