# -- code: utf-8 --
from __future__ import absolute_import

from django.test import TestCase
from django.test.client import Client
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse

from .models import X509UserMapping
from .auth_backend import is_X509_authenticated


class X509UserMappingTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test", password="test")
        self.notuser = User.objects.create(username="nottest")
        self.dn = "AwesomeDN"
        self.mapping = X509UserMapping.objects.create(
            user=self.user,
            cert_dn=self.dn)
        self.notmapping = X509UserMapping.objects.create(
            user=self.notuser,
            cert_dn='not'+self.dn)
        self.c = Client()

    def test_programmatic_auth(self):
        """
        Test programmatic authentication.  Exercises the authentication
        backend directly.
        """

        user = authenticate(dn=self.dn, verified='SUCCESS')
        self.assertEqual(user, self.user)

    def test_programmatic_bad_auth(self):
        """
        Test programmatic authentication.  Exercises the authentication
        backend directly.  Should be None.
        """

        user = authenticate(dn=self.dn)
        self.assertEqual(user, None)

    def test_no_auth_views(self):
        """
        Test going to a location that requires authentication.
        """

        # @login_required, so 302 (not logged in)
        response = self.c.get(reverse('x509_auth_list'),
                              HTTP_X_SSL_USER_DN=self.dn,
                              HTTP_X_SSL_AUTHENTICATED='SUCCESS')
        self.assertEqual(response.status_code, 302)

    def test_auth_baddn_views(self):
        """
        Test sending an unmapped X.509 Subject (DN).
        """

        self.c.get(reverse('x509_auth_auth'),
                   {'next': reverse('x509_auth_list')},
                   HTTP_X_SSL_USER_DN=self.dn+'X',
                   HTTP_X_SSL_AUTHENTICATED='SUCCESS',
                   follow=True)

        # @login_required, so 302 (not logged in)
        response = self.c.get(reverse('x509_auth_list'),
                              HTTP_X_SSL_USER_DN=self.dn+'X',
                              HTTP_X_SSL_AUTHENTICATED='SUCCESS')
        self.assertEqual(response.status_code, 302)

    def test_auth_invalid_ssl_views(self):
        """
        Test sending an invalid cert (even if the Subject is good).
        """

        self.c.get(reverse('x509_auth_auth'),
                   {'next': reverse('x509_auth_list')},
                   HTTP_X_SSL_USER_DN=self.dn,
                   HTTP_X_SSL_AUTHENTICATED='ANYTHING_NOT_SUCCESS',
                   follow=True)

        # @login_required, so 302 (not logged in)
        response = self.c.get(reverse('x509_auth_list'),
                              HTTP_X_SSL_USER_DN=self.dn,
                              HTTP_X_SSL_AUTHENTICATED='ANYTHING_NOT_SUCCESS')
        self.assertEqual(response.status_code, 302)

    def test_auth_success_views(self):
        """
        Test actually working.
        """

        response = self.c.get(reverse('x509_auth_auth'),
                              {'next': reverse('x509_auth_list')},
                              HTTP_X_SSL_USER_DN=self.dn,
                              HTTP_X_SSL_AUTHENTICATED='SUCCESS')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.endswith(reverse('x509_auth_list')), True)

        # If logged in, will be 200
        response = self.c.get(reverse('x509_auth_list'),
                              HTTP_X_SSL_USER_DN=self.dn,
                              HTTP_X_SSL_AUTHENTICATED='SUCCESS')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('You are using this new certificate:',
                         response.content)

    def test_auth_success_views_no_next(self):
        """
        Test actually working, but with out next parameter.
        """

        response = self.c.get(reverse('x509_auth_auth'),
                              HTTP_X_SSL_USER_DN=self.dn,
                              HTTP_X_SSL_AUTHENTICATED='SUCCESS')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.endswith(reverse('x509_auth_list')), False)

        # If logged in, will be 200
        response = self.c.get(reverse('x509_auth_list'),
                              HTTP_X_SSL_USER_DN=self.dn,
                              HTTP_X_SSL_AUTHENTICATED='SUCCESS')
        self.assertEqual(response.status_code, 200)

    def test_auth_views_missing_header(self):
        """
        Test trying to auth while missing a header.
        """

        # Unsuccessful login will NOT redirect, ergo, 200
        response = self.c.get(reverse('x509_auth_auth'),
                              {'next': reverse('x509_auth_list')},
                              HTTP_X_SSL_AUTHENTICATED='SUCCESS')
        self.assertEqual(response.status_code, 200)

    def test_list_view_new_cert(self):
        """
        Test actually working, but then send new cert (prompts to add).
        """

        self.test_auth_success_views()

        # If logged in, will be 200
        response = self.c.get(reverse('x509_auth_list'),
                              HTTP_X_SSL_USER_DN=self.dn+'X',
                              HTTP_X_SSL_AUTHENTICATED='SUCCESS')
        self.assertEqual(response.status_code, 200)
        self.assertIn('You are using this new certificate:', response.content)

    def test_delete_mapping(self):
        """
        Test deleting a mapping.
        """

        self.test_auth_success_views()
        response = self.c.get(reverse('x509_auth_delete', kwargs={'pk': 1}),
                              HTTP_X_SSL_USER_DN=self.dn,
                              HTTP_X_SSL_AUTHENTICATED='SUCCESS')
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'Are you sure you want to delete "{0}"'.format(str(self.mapping)),
            response.content)

    def test_delete_mapping_not_you(self):
        """
        Test deleting a mapping of another users.
        """

        self.test_auth_success_views()
        response = self.c.get(reverse('x509_auth_delete', kwargs={'pk': 2}),
                              HTTP_X_SSL_USER_DN=self.dn,
                              HTTP_X_SSL_AUTHENTICATED='SUCCESS')
        self.assertEqual(response.status_code, 404)
        self.assertNotIn(
            'Are you sure you want to delete',
            response.content)

    def test_create_form_bad(self):
        """
        Test posting to the create form, bad input.
        """

        self.test_auth_success_views()
        response = self.c.post(reverse('x509_auth_map'), {'NOTcert_dn': 'OtherCern'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('This field is required.', response.content)

    def test_create_form_non_unique(self):
        """
        Test posting to the create form, but with non-unique DN.
        """

        self.test_auth_success_views()
        response = self.c.post(reverse('x509_auth_map'), {'cert_dn':
                                                self.mapping.cert_dn})
        self.assertEqual(response.status_code, 200)
        self.assertIn('X509 user mapping with this Cert dn already exists.',
                      response.content)

    def test_create_form_good(self):
        """
        Test posting to the create form, good input.
        """

        self.test_auth_success_views()
        response = self.c.post(reverse('x509_auth_map'), {'cert_dn': 'OtherCern'})
        self.assertEqual(response.status_code, 302)

    def test_is_auth_backend(self):
        """
        Test our decorator function and auth test utility function.
        """
        factory = RequestFactory()
        request = factory.get('/x509/list')
        request.user = self.user
        self.assertEqual(request.user.is_authenticated(), True)

        # Jam a session in here.  Dictionaries are close enough to sessions.
        # Only your hair dresser knows for sure.
        request.session = {}
        request.session['_auth_user_backend'] = (
            'x509_auth.auth_backend.AuthenticationBackend')

        self.assertEqual(is_X509_authenticated(request), True)

    def test_is_auth_backend_wrong_backend(self):
        """
        Test our decorator function and auth test utility function, when
        someone is NOT using our backend.
        """
        factory = RequestFactory()
        request = factory.get('/x509/list')
        request.user = self.user
        self.assertEqual(request.user.is_authenticated(), True)

        # Jam a session in here.  Dictionaries are close enough to sessions.
        # Only your hair dresser knows for sure.
        request.session = {}
        request.session['_auth_user_backend'] = 'some.other.Backend'

        self.assertEqual(is_X509_authenticated(request), False)

    def test_is_auth_backend_unauthed(self):
        """
        Test our decorator function and auth test utility function when someone
        is not logged in.
        """
        factory = RequestFactory()
        request = factory.get('/x509/list')
        request.user = AnonymousUser()

        self.assertEqual(request.user.is_authenticated(), False)

        self.assertEqual(is_X509_authenticated(request), False)

    def test_is_auth_backend_key_error(self):
        """
        Test our decorator function and auth test utility function.  Don't
        include the required session key.  This should never happen.
        """
        factory = RequestFactory()
        request = factory.get('/x509/list')
        request.user = self.user
        self.assertEqual(request.user.is_authenticated(), True)

        # Jam a session in here.  Dictionaries are close enough to sessions.
        # Only your hair dresser knows for sure.
        request.session = {}
        self.assertEqual(is_X509_authenticated(request), False)

    def test_auth_success_template_tag(self):
        """
        Test template tag.
        """

        self.test_auth_success_views()
        response = self.c.get(reverse('x509_auth_map'))
        self.assertIn("TEST: True", response.content)

    # sans django.core.context_processors.request
    @override_settings(TEMPLATE_CONTEXT_PROCESSORS=(
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
    ))
    def test_auth_fail_template_tag(self):
        """
        Test template tag, but with out the needed context processor.
        """

        self.test_auth_success_views()
        response = self.c.get(reverse('x509_auth_map'))
        self.assertIn("TEST: False", response.content)
