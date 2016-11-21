# -- code: utf-8 --
from __future__ import absolute_import

from .models import X509UserMapping


class X509ContextMixin(object):

    def x509_modify_context(self, context, request, user):
        """
        Some what of a utility method.  Designed to be called by FBVs.  Does
        not rely on 'self'.  Modifies context in place.
        """
        if (('HTTP_X_SSL_USER_DN' in request.META) and
           ('HTTP_X_SSL_AUTHENTICATED' in request.META)):
            # A key is asserted, see if we already have it
            certs = X509UserMapping.objects.filter(
                user=user,
                cert_dn=request.META['HTTP_X_SSL_USER_DN'])
            if not certs.exists():
                for k in ['HTTP_X_SSL_USER_DN', 'HTTP_X_SSL_AUTHENTICATED']:
                    # Put in the context for possible addition
                    context[k] = request.META[k]

    def get_context_data(self, **kwargs):
        context = super(X509ContextMixin, self).get_context_data(**kwargs)
        self.x509_modify_context(context, self.request, self.request.user)
        return context
