import unittest


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from eitbapi import main

        app = main({})
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get("/", status=200)
        self.assertTrue(b"Pyramid" not in res.body)
