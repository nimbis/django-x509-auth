# -- code: utf-8 --
from __future__ import absolute_import

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from x509_auth.views import X509AuthView, X509CreateView
from x509_auth.views import X509ListView, X509DeleteView
from x509_auth.auth_backend import X509_required

urlpatterns = patterns(
    '',
    url(r'^auth/$', X509AuthView.as_view(), name='auth'),
    url(r'^map/$',
        login_required(X509CreateView.as_view()),
        name='map'),
    url(r'^map-test/$',
        X509_required(X509CreateView.as_view()),
        name='map2'),
    url(r'^list/$',
        login_required(X509ListView.as_view()),
        name='list'),
    url(r'^delete/(?P<pk>\d+)$',
        login_required(X509DeleteView.as_view()),
        name='delete'),
)
