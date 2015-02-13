# -- code: utf-8 --
from __future__ import absolute_import

from django.conf.urls import patterns, url

from .views import CertAuthView, CertCreateView, CertListView

urlpatterns = patterns(
    '',
    url(r'^auth/$', CertAuthView.as_view(), name='auth'),
    url(r'^map/$', CertCreateView.as_view(), name='map'),
    url(r'^list/$', CertListView.as_view(), name='list'),
)
