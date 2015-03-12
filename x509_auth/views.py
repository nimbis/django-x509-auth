# -- code: utf-8 --
from __future__ import absolute_import

import logging

from django.contrib.auth import login, authenticate
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy

from .models import X509UserMapping
from .auth_backend import is_X509_authed

logger = logging.getLogger(__name__)


class X509AuthView(TemplateView):
    """
    View to look for HTTP headers and if found, map and authenticate a user
    (if possible)
    """

    template_name = "x509_auth/auth.html"

    def get_context_data(self, **kwargs):
        context = super(X509AuthView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        try:
            dn = request.META['HTTP_X_SSL_USER_DN']
            verified = request.META['HTTP_X_SSL_AUTHENTICATED']
        except KeyError:
            # HTTP headers not set
            messages.error(self.request,
                           'We did not get any certificate information.  '
                           'Please verify that your user certificate to '
                           'loaded in your browser.')
            return self.render_to_response(context)

        # requires our backend
        user = authenticate(dn=dn, verified=verified)
        print "RESULT: is_X509_authed {0}".format(is_X509_authed(user))
        if user is not None:
            login(request, user)
            try:
                return HttpResponseRedirect(request.GET['next'])
            except KeyError:
                return HttpResponseRedirect('/')
        else:
            for k in ['HTTP_X_SSL_USER_DN', 'HTTP_X_SSL_AUTHENTICATED']:
                context[k] = request.META[k]
            return self.render_to_response(context)


class X509ListView(ListView):
    """
    Lists out certificates owned by request.user.  If there is a certificate
    asserted in the request, and we don't have record of it, offers to add it.
    """

    model = X509UserMapping
    template_name = 'x509_auth/list.html'

    def get_context_data(self, **kwargs):
        context = super(X509ListView, self).get_context_data(**kwargs)
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

    def get_queryset(self):
        """
        Limit query set to logged in user
        """
        return self.model.objects.filter(user=self.request.user)


class X509CreateView(CreateView):
    """
    Does X509UserMapping creation.  Forces the user attribute to be the
    user that is currently logged in.
    """

    model = X509UserMapping
    template_name = 'x509_auth/create.html'
    fields = ['cert_dn']
    success_url = reverse_lazy('list')

    def form_valid(self, form):
        """
        Force user to logged in user
        """
        form.instance.user = self.request.user
        return super(X509CreateView, self).form_valid(form)


class X509DeleteView(DeleteView):
    """
    Performs delete.  User will get a confirmation, and user may only
    delete mappings owned by themselves.
    """

    model = X509UserMapping
    template_name = 'x509_auth/delete.html'
    success_url = reverse_lazy('list')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(X509DeleteView, self).get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj
