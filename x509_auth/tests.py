# -- code: utf-8 --
from __future__ import absolute_import

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

from .models import UserCertMapping

class UserCertMappingTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.dn = "AwesomeDN"

    def create_mapping(self):
        self.mapping = UserCertMapping.object.create(
            user=self.user,
            cert_dn=self.dn)

    def try_auth(self):
        user = authenticate(dn=self.dn, verified='SUCCESS')
        self.assertEqual(user, self.User)
