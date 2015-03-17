# -- code: utf-8 --
from __future__ import absolute_import

from django.contrib import admin
from .models import X509UserMapping


class X509UserMappingAdmin(admin.ModelAdmin):
    """
    Admin model for X509UserMapping
    """
    list_display = ('user','cert_dn')

admin.site.register(X509UserMapping, X509UserMappingAdmin)
