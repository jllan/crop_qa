from django.test import TestCase
import unittest
from django.test import Client

class SimpleTest(unittest.TestCase):
    def test_index(self):
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        client = Client()
        search_qs = [
            '',
            123,
            '水稻如何防治稻瘟病',
            '水稻收割'
        ]
        for q in search_qs:
            response = client.post('/search/', {'search_for': q})
            print(response.status_code)
            # self.assertEqual(response.status_code, 200)

