# -- code: utf-8 --
from __future__ import absolute_import

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required, user_passes_test

from .views import X509AuthView, X509CreateView, X509ListView, X509DeleteView
from .auth_backend import is_X509_authed

urlpatterns = patterns(
    '',
    url(r'^auth/$', X509AuthView.as_view(), name='auth'),
    url(r'^map/$',
        login_required(X509CreateView.as_view()),
        name='map'),
    url(r'^map2/$',
        user_passes_test(X509CreateView.as_view(), is_X509_authed),
        name='map'),
    url(r'^map3/$',
        login_required(X509CreateView.as_view()),
        name='map'),
    url(r'^list/$',
        login_required(X509ListView.as_view()),
        name='list'),
    url(r'^delete/(?P<pk>\d+)$',
        login_required(X509DeleteView.as_view()),
        name='delete'),
)
