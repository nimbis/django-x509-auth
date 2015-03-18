#!/usr/bin/env python

from setuptools import setup, find_packages

# setup the project
setup(
    name="django-x509-auth",
    version="1.0.0",
    author="Nimbis Services, Inc.",
    author_email="info@nimbisservices.com",
    description="Django app to facilitate mapping X.509 certificates to User "
    "models.",
    license="BSD",
    packages=find_packages(exclude=["tests", ]),
    zip_safe=False,
    include_package_data=True,
    test_suite="tests.main",
    install_requires=[
        'Django',
    ],
)
