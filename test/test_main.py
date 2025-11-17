
import unittest
import json
import os
from main import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')

    def test_generate_api_no_api_key(self):
        # Temporarily set GEMINI_API_KEY to 'TODO' to simulate missing key
        original_api_key = os.environ['GEMINI_API_KEY']     
        os.environ['GEMINI_API_KEY'] = 'TODO'
        try:
            
            response = self.app.post('/api/generate', json={"request_json" : {}})
            # TODO add some asserts
        finally:
            # Restore the original API key
            os.environ['GEMINI_API_KEY'] = original_api_key

    # def test_generate_api_invalid_request(self):
    #     response = self.app.post('/api/generate', json={"contents" : "this is a test"})
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertIn('error', data)

    # def test_serve_static_file(self):
    #     response = self.app.get('/style.css')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.content_type, 'text/css; charset=utf-8')

    def test_generate_api(self):
        response = self.app.post('/api/generate', json={"request_json" : {"test campaign"}})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
if __name__ == '__main__':
    unittest.main()
