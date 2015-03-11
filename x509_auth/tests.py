# -- code: utf-8 --
from __future__ import absolute_import

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.conf import settings
from django.core.urlresolvers import reverse

from .models import X509UserMapping


class X509UserMappingTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.dn = "AwesomeDN"
        self.mapping = X509UserMapping.objects.create(
            user=self.user,
            cert_dn=self.dn)
        self.c = Client()

    def test_programmatic_auth(self):
        """
        Test programmatic authentication.  Excercises the authentication
        backend directly.
        """
        user = authenticate(dn=self.dn, verified='SUCCESS')
        self.assertEqual(user, self.user)

    def test_no_auth_views(self):
        """
        Test going to a location that requires authentication.
        """
        # @login_required, so 302 (not logged in)
        response = self.c.get(reverse('list'),
                              HTTP_X_SSL_USER_DN=self.dn,
                              HTTP_X_SSL_AUTHENTICATED='SUCCESS')
        self.assertEqual(response.status_code, 302)

    def test_auth_baddn_views(self):
        """
        Test sending an unmapped X.509 Subject (DN)
        """
        self.c.get(reverse('auth'),
                   {'next': reverse('list')},
                   HTTP_X_SSL_USER_DN=self.dn+'X',
                   HTTP_X_SSL_AUTHENTICATED='SUCCESS',
                   follow=True)

        # @login_required, so 302 (not logged in)
        response = self.c.get(reverse('list'),
                              HTTP_X_SSL_USER_DN=self.dn+'X',
                              HTTP_X_SSL_AUTHENTICATED='SUCCESS')
        self.assertEqual(response.status_code, 302)

    def test_auth_invalid_views(self):
        """
        Test sending an invalid cert (even if the Subject is good)
        """
        self.c.get(reverse('auth'),
                   {'next': reverse('list')},
                   HTTP_X_SSL_USER_DN=self.dn,
                   HTTP_X_SSL_AUTHENTICATED='ANYTHING_NOT_SUCCESS',
                   follow=True)

        # @login_required, so 302 (not logged in)
        response = self.c.get(reverse('list'),
                              HTTP_X_SSL_USER_DN=self.dn,
                              HTTP_X_SSL_AUTHENTICATED='ANYTHING_NOT_SUCCESS')
        self.assertEqual(response.status_code, 302)

    def test_auth_success_views(self):
        """
        Test actually working.
        """
        self.c.get(reverse('auth'),
                   {'next': reverse('list')},
                   HTTP_X_SSL_USER_DN=self.dn,
                   HTTP_X_SSL_AUTHENTICATED='SUCCESS',
                   follow=True)

        # If logged in, will be 200
        response = self.c.get(reverse('list'),
                              HTTP_X_SSL_USER_DN=self.dn,
                              HTTP_X_SSL_AUTHENTICATED='SUCCESS')
        self.assertEqual(response.status_code, 200)
