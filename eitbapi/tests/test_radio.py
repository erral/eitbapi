import json
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
        res = self.testapp.get('/radio', status=200)
        members = json.loads(res.text).get('member', [])
        for member in members[:2]:
            # Workaround to remove localhost prefix from id url
            url = member.get('@id').replace('http://localhost', '')
            result = self.testapp.get(url, status=200)
            self.assertTrue(result.headers.get('Content-type').startswith('application/json'))

    def test_radio_program_types_list(self):
        res = self.testapp.get('/radio-program-type-list', status=200)
        self.assertTrue(res.headers.get('Content-type').startswith('application/json'))

    def test_radio_program_type_playlist(self):
        res = self.testapp.get('/radio-program-type-list', status=200)
        members = json.loads(res.text).get('member', [])
        for member in members[:2]:
            # Workaround to remove localhost prefix from id url
            url = member.get('@id').replace('http://localhost', '')
            result = self.testapp.get(url, status=200)
            self.assertTrue(result.headers.get('Content-type').startswith('application/json'))

    def test_radio_station_list(self):
        res = self.testapp.get('/radio-stations', status=200)
        self.assertTrue(res.headers.get('Content-type').startswith('application/json'))

    def test_radio_station_program_list(self):
        res = self.testapp.get('/radio-stations', status=200)
        members = json.loads(res.text).get('member', [])
        for member in members:
            # Workaround to remove localhost prefix from id url
            url = member.get('@id').replace('http://localhost', '')
            result = self.testapp.get(url, status=200)
            self.assertTrue(result.headers.get('Content-type').startswith('application/json'))
