import unittest
import json

from .app import app

PATH = '/servicio/v1/prediccion/'

ENDPOINTS = [
    {'endpoint': '24horas', 'periods': 24},
    {'endpoint': '48horas', 'periods': 48},
    {'endpoint': '72horas', 'periods': 72}
]

class TestAppV1(unittest.TestCase): 
    def setUp(self):
        self.client = app.test_client()

    def test_endpoints(self):
        for info in ENDPOINTS:
            response = self.client.get(PATH + info['endpoint'])
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('periods', data)
            self.assertIn('prediction', data)
            self.assertEqual(data['periods'], info['periods'])