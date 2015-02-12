# -- code: utf-8 --
from __future__ import absolute_import

import logging

from django.contrib.auth import login
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.contrib import messages

from .models import UserCertMapping

logger = logging.getLogger(__name__)


class CertAuthView(TemplateView):
    '''
    View to look for HTTP headers and if found, map and authenticate a user
    (if possible)
    '''

    template_name = "usercert_mapping/cert_auth.html"

    def get_context_data(self, **kwargs):
        context = super(CertAuthView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        try:
            dn = request.META['HTTP_X_SSL_USER_DN'])
            verified = request.META['HTTP_X_SSL_AUTHENTICATED'])
        except KeyError:
            # HTTP headers not set
            messages.error(self.request,
                'We did not get any certificate information.  Please verify '
                'that your user certificate to loaded in your browser.')
            return self.render_to_response(context)

        # requires our backend
        user = authenticate(dn=dn, verified=verified)
        if user is not None:
            login(request, user)
            if 'next' in request.GET:
                return HttpResponseRedirect(request.GET['next'])
            else:
                return HttpResponseRedirect('/')
        else:
            for k in ['HTTP_X_SSL_USER_DN', 'HTTP_X_SSL_AUTHENTICATED']:
                # no hyphens in context variables
                context[k] = request.META[k]
            return self.render_to_response(context)


class CertMapView(TemplateView):
    '''
    View to map X.509 cert to a User
    '''

    template_name = "usercert_mapping/cert_auth.html"

    def get_context_data(self, **kwargs):
        context = super(CertMapView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        for k in request.META:
            print k, request.META[k]
            context[k] = request.META[k]
        print context
        return self.render_to_response(context)
