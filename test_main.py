
import unittest
import json
from main import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')

    def test_generate_api_no_api_key(self):
        # Temporarily set API_KEY to 'TODO' to simulate missing key
        from main import API_KEY
        original_api_key = API_KEY
        try:
            # This is a bit of a hack to modify the global variable in the main module
            import main
            main.API_KEY = 'TODO'
            response = self.app.post('/api/generate', json={})
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('To get started, get an API key', data['error'])
        finally:
            # Restore the original API key
            main.API_KEY = original_api_key

    def test_generate_api_invalid_request(self):
        response = self.app.post('/api/generate', json={"contents" : "this is a test"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_serve_static_file(self):
        response = self.app.get('/style.css')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/css; charset=utf-8')

    def test_generate_api(self):
        response = self.app.post('/api/generate', json={"contents" : "test campaign"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
if __name__ == '__main__':
    unittest.main()
