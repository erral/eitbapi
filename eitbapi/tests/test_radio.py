import unittest


class RadioTests(unittest.TestCase):
    def setUp(self):
        from eitbapi import main
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_radio(self):
        res = self.testapp.get('/radio', status=200)
        self.assertTrue(res.headers.get('Content-type').startswith('application/json'))

    def test_radio_playlist(self):
        res = self.testapp.get('/rplaylist/es/radio/radio-vitoria/5-minutos-mas/4346748/', status=200)
        self.assertTrue(res.headers.get('Content-type').startswith('application/json'))
