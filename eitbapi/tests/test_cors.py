import unittest
from webtest import TestApp

class CORSTests(unittest.TestCase):
    def setUp(self):
        from eitbapi import main
        self.app = main({})
        self.testapp = TestApp(self.app)

    def test_acces_control_allow_origing_is_present(self):
        headers = {'Origin': '*'}
        res = self.testapp.get('/program-type-news', status=200, headers=headers)
        acao = res.headers.get('Access-Control-Allow-Origin')
        self.assertTrue(acao)

