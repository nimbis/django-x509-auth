# -- code: utf-8 --
from __future__ import absolute_import

from .models import X509UserMapping


class X509ContextMixin(object):
    def get_context_data(self, **kwargs):
        context = super(X509ContextMixin, self).get_context_data(**kwargs)
        if (('HTTP_X_SSL_USER_DN' in self.request.META) and
           ('HTTP_X_SSL_AUTHENTICATED' in self.request.META)):
            # A key is asserted, see if we already have it
            certs = X509UserMapping.objects.filter(
                user=self.request.user,
                cert_dn=self.request.META['HTTP_X_SSL_USER_DN'])
            if not certs.exists():
                for k in ['HTTP_X_SSL_USER_DN', 'HTTP_X_SSL_AUTHENTICATED']:
                    # Put in the context for possible addition
                    context[k] = self.request.META[k]
        return context
