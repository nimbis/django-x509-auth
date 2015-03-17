# -- code: utf-8 --
from __future__ import absolute_import

import logging
from functools import wraps

from django.contrib.auth.backends import ModelBackend
from django.utils.decorators import available_attrs
from django.core.urlresolvers import reverse
from django.contrib.auth.views import redirect_to_login

from .models import X509UserMapping

logger = logging.getLogger(__name__)


class AuthenticationBackend(ModelBackend):

    def authenticate(self, **credentials):
        """
        Try to look up User in X509UserMaps, returning None if not found
        """

        if 'dn' not in credentials or 'verified' not in credentials:
            return None

        if credentials['verified'] != 'SUCCESS':
            return None

        try:
            return X509UserMapping.objects.get(cert_dn=credentials['dn']).user
        except X509UserMapping.DoesNotExist:
            return None


def is_X509_authed(request):
    """
    Check how this user authenticated (did they use our backend?)
    """
    if not request.user.is_authenticated():
        return False
    try:
        if (request.session['_auth_user_backend'] !=
                'x509_auth.auth_backend.AuthenticationBackend'):
            return False
    except KeyError:
        # Odd.. we're authed with out a backend.
        logger.error("is_X509_authed got a user that was logged in but some "
                     "how did not have '_auth_user_backend' in their session")
        return False

    return True


def X509_required(view_func):
    """
    Decorator to force that a user has authenticated with our backend.
    Redirects them to our auth page if not.
    """

    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if not is_X509_authed(request):
            return redirect_to_login(request.get_full_path(), reverse('auth'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view
