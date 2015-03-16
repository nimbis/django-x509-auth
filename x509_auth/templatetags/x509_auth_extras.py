# -- code: utf-8 --
from __future__ import absolute_import

import logging

from django import template

from x509_auth.auth_backend import is_X509_authed as authed_backend

logger = logging.getLogger(__name__)

register = template.Library()


@register.assignment_tag(takes_context=True)
def is_X509_authed(context):
    try:
        return authed_backend(context['request'])
    except:
        logger.error("'request' not found in context.  Make sure you have the"
                     " right context processors in place (see docs)")
        return False
