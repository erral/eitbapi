import json
import unittest

class TVTests(unittest.TestCase):
    def setUp(self):
        from eitbapi import main
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_programs(self):
        res = self.testapp.get('/playlist', status=200)
        self.assertTrue(res.headers.get('Content-type').startswith('application/json'))

    def test_program_playlist(self):
        res = self.testapp.get('/playlist', status=200)
        members = json.loads(res.text).get('member', [])
        for member in members[:2]:
            # Workaround to remove localhost prefix from id url
            url = member.get('@id').replace('http://localhost', '')
            result = self.testapp.get(url, status=200)
            self.assertTrue(result.headers.get('Content-type').startswith('application/json'))

    def test_program_playlist_episode(self):
        res = self.testapp.get('/playlist', status=200)
        members = json.loads(res.text).get('member', [])
        for member in members[:1]:
            # Workaround to remove localhost prefix from id url
            url = member.get('@id').replace('http://localhost', '')
            result = self.testapp.get(url, status=200)
            submembers = json.loads(result.text).get('member', [])
            for submember in submembers[:2]:
                # Workaround to remove localhost prefix from id url
                suburl = submember.get('@id').replace('http://localhost', '')
                subresult = self.testapp.get(suburl, status=200)
                self.assertTrue(subresult.headers.get('Content-type').startswith('application/json'))

    def test_program_type_list(self):
        res = self.testapp.get('/program-type-list', status=200)
        self.assertTrue(res.headers.get('Content-type').startswith('application/json'))

    def test_program_type_news(self):
        res = self.testapp.get('/program-type-news', status=200)
        self.assertTrue(res.headers.get('Content-type').startswith('application/json'))

    def test_program_list_per_type(self):
        res = self.testapp.get('/program-type-list', status=200)
        members = json.loads(res.text).get('member', [])
        for member in members:
            # Workaround to remove localhost prefix from id url
            url = member.get('@id').replace('http://localhost', '')
            result = self.testapp.get(url, status=200)
            self.assertTrue(result.headers.get('Content-type').startswith('application/json'))
