# -- code: utf-8 --
from __future__ import absolute_import

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import X509AuthView, X509CreateView, X509ListView, X509DeleteView

urlpatterns = [
    url(r'^auth/$', X509AuthView.as_view(), name='x509_auth_auth'),
    url(r'^map/$',
        login_required(X509CreateView.as_view()),
        name='x509_auth_map'),
    url(r'^list/$',
        login_required(X509ListView.as_view()),
        name='x509_auth_list'),
    url(r'^delete/(?P<pk>\d+)$',
        login_required(X509DeleteView.as_view()),
        name='x509_auth_delete'),
]
