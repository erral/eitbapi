import unittest

from pyramid import testing


class TutorialViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_index(self):
        from eitbapi.views import index

        request = testing.DummyRequest()
        response = index(request)
        self.assertEqual(type(response), dict)
