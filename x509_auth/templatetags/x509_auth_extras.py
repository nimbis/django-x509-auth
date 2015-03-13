# -- code: utf-8 --
from __future__ import absolute_import

from django import template

from x509_auth.auth_backend import is_X509_authed

register = template.Library()


@register.assignment_tag(takes_context=True)
def is_X509_authed(context):
    request = context['request']
    return is_X509_authed(request)
