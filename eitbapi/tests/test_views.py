from pyramid import testing
import unittest


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from eitbapi import main
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue(b'Pyramid' not in res.body)

    def test_programs(self):
        res = self.testapp.get('/playlist', status=200)
        self.assertTrue(res.headers.get('Content-type').startswith('application/json'))

    def test_program_playlist(self):
        res = self.testapp.get('/playlist/4105019553001', status=200)
        self.assertTrue(res.headers.get('Content-type').startswith('application/json'))

    def test_program_playlist_episode(self):
        res = self.testapp.get('/episode/heltzean/927/23221/heltzean', status=200)
        self.assertTrue(res.headers.get('Content-type').startswith('application/json'))

    def test_radio(self):
        res = self.testapp.get('/radio', status=200)
        self.assertTrue(res.headers.get('Content-type').startswith('application/json'))

    def test_radio_playlist(self):
        res = self.testapp.get('/rplaylist/es/radio/radio-vitoria/5-minutos-mas/4346748/', status=200)
        self.assertTrue(res.headers.get('Content-type').startswith('application/json'))
