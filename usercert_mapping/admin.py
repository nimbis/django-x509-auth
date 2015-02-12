# -- code: utf-8 --
from __future__ import absolute_import

from django.contrib import admin
from .models import UserCertMapping


class UserCertMappingAdmin(admin.ModelAdmin):
    '''
    Admin model for UserCertMapping
    '''
    pass

admin.site.register(UserCertMapping, UserCertMappingAdmin)
