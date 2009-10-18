import unittest
from django.conf import settings
from django.db.models import get_app, get_apps
from django.test import _doctest as doctest
from django.test.utils import setup_test_environment, teardown_test_environment
from django.test.testcases import OutputChecker, DocTestRunner, TestCase
from django.test.simple import *

from pony_build.client.pony_client import send, get_arch


def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    """
    Run the unit tests for all the test labels in the provided list.
    Labels must be of the form:
     - app.TestClass.test_method
        Run a single specific test method
     - app.TestClass
        Run all the test methods in a given class
     - app
        Search for doctests and unittests in the named application.

    When looking for tests, the test runner will look in the models and
    tests modules for the application.

    A list of 'extra' tests may also be provided; these tests
    will be added to the test suite.

    Returns the number of tests that failed.
    """
    setup_test_environment()

    settings.DEBUG = False
    suite = unittest.TestSuite()

    if test_labels:
        for label in test_labels:
            if '.' in label:
                suite.addTest(build_test(label))
            else:
                app = get_app(label)
                suite.addTest(build_suite(app))
    else:
        for app in get_apps():
            #run_tests(build_suite(app))
            suite.addTest(build_suite(app))

    for test in extra_tests:
        suite.addTest(test)

    suite = reorder_suite(suite, (TestCase,))

    old_name = settings.DATABASE_NAME
    from django.db import connection
    connection.creation.create_test_db(verbosity, autoclobber=not interactive)
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    connection.creation.destroy_test_db(old_name, verbosity)

    teardown_test_environment()

    def insert_failure(failed_apps, app, failure):
        if failed_apps.has_key(app):
            failed_apps[app].append(failure)
        else:
            failed_apps[app] = [failure]

    def increment_app(all_apps, app):
        if all_apps.has_key(app):
            all_apps[app] += 1
        else:
            all_apps[app] = 1

    def get_app_name_from_test(test):
        app = test.__module__.split('.tests.')[0]
        if not app:
            app = test.__module__.split('.models.')[0]
        if not app:
            app = test.__module__.split('.')[0]
        return app


    failed_apps = {}
    all_apps = {}
    for test in suite._tests:
        test_app = get_app_name_from_test(test)
        increment_app(all_apps, test_app)
    for failure in result.failures + result.errors:
        test = failure[0]
        output = failure[1]
        app = get_app_name_from_test(test)
        insert_failure(failed_apps, app, failure)

    arch = get_arch()
    for app in all_apps:
        success = app not in failed_apps.keys()
        if app in failed_apps:
            errout = '\n'.join([failure[1] for failure in failed_apps[app]])
        else:
            errout = "%s Passed" % all_apps[app]
        result_list = []
        result_list.append({'awesome_tests':
                                {'commands': ['woot'] },
                                'status': True,
                                'errout': errout
                            })
        client_info = dict(package=app, arch=arch, success=success)
        send('http://djangoproject.com:9999/xmlrpc', (client_info, result_list), tags=['django_test_runner'])



    return len(result.failures) + len(result.errors)
