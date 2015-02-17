# -- code: utf-8 --
from __future__ import absolute_import

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import CertAuthView, CertCreateView, CertListView, CertDeleteView

urlpatterns = patterns(
    '',
    url(r'^auth/$', CertAuthView.as_view(), name='auth'),
    url(r'^map/$',
        login_required(CertCreateView.as_view()),
        name='map'),
    url(r'^list/$',
        login_required(CertListView.as_view()),
        name='list'),
    url(r'^delete/(?P<pk>\d+)$',
        login_required(CertDeleteView.as_view()),
        name='delete'),
)
