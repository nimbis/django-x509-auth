django-x509-auth
================

Django app to facilitate mapping X.509 certificates to User models

[![Build Status](https://api.travis-ci.org/nimbis/django-x509-auth.svg?branch=master)](https://api.travis-ci.org/nimbis/django-x509-auth.svg)

Requirements
------------

* django >= 1.6

Installation
------------

* Run `pip install django-x509-auth` or download this package and run `python setup.py install`

* Ensure that `x509_auth` is in your INSTALLED APPS

* Run `syncdb` or `migrate x509_auth` if you have South installed.

* In order to authenticate people directly with certificate mappings, you must have `'x509_auth.auth_backend.AuthenticationBackend'` in `settings.AUTHENTICATION_BACKENDS`

* In order to use the template tag, you must have `'django.core.context_processors.request'` in `settings.TEMPLATE_CONTEXT_PROCESSORS`

* Your web server must set two HTTP headers, `HTTP_X_SSL_AUTHENTICATED` and `HTTP_X_SSL_USER_DN`.  See http://nategood.com/client-side-certificate-authentication-in-ngi for configuring Nginx to do client side authentication.  Note: the link uses CGI parameters instead of HTTP headers.  Hint:

    proxy_set_header X-SSL-User-DN   $ssl_client_s_dn;
    proxy_set_header X-SSL-Authenticated $ssl_client_verify

Overview
--------

django-x509-auth offers CRUD and auth views around a simple model, mapping a
django User model to an X.509 subject.  We rely on the web server to handle
validation of client side certificates.  For this reason you must make sure you
protect your local Django instance from direct access.

A template tag of `is_X509_authed` is available.  This will returns True if you
have authenticated against the provided backend, and False otherwise.

    {% is_X509_authed as authed %}
    TEST: {{ authed }}

A decorator of `X509_required` is available.  It behaves much like
`login_required` in that it will take you to the auth view (which supports
'next' as a GET parameter).
