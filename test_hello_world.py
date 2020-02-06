from webserver import hello_world
import unittest

class TestHelloWorld(unittest.TestCase):

    def setUp(self):
        self.app = hello_world.app.test_client()
        self.app.testing = True

    def test_status_code(self):
        response = self.app.get('/hello')
        self.assertEqual(response.status_code, 200)
        
    def test_greeting_message(self):
        greeting = 'Hello World from BenchSci!'
        self.assertEqual(hello_world.helloIndex(), greeting)
        

if __name__ == '__main__':
    unittest.main()
