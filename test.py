import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Users, Books, Exchange

admin = os.environ['ADMIN_TOKEN']
reader = os.environ['READER_TOKEN']


# testdb = os.environ['TEST_DATABASE_URL']


class ReadMeetReadTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.headers_admin = {
            'Content-Type': 'application/json',
            'Authorization': admin}
        self.headers_reader = {
            'Content-Type': 'application/json',
            'Authorization': reader}

    def test_post_user(self):
        res = self.client().post(
            '/user',
            json={
                "name": "TestUser",
                "zip_code": "1111",
                "city": "Delhi",
                "country": "India"
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_user_fail(self):
        res = self.client().post(
            '/user',
            json={
                "name": "TestUser",
                "zip_code": "1111",
                "city": "Delhi"
            })
        data = json.loads(res.data)
        self.assertEqual(data['message'], 'You seem to have missed some data, Provide name, zip_code, city and country')

    def test_get_users(self):
        res = self.client().get('/users')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_user(self):
        res = self.client().delete('/user/1',  # TODO specify existing user id in URL to make test return OK
                                   headers=self.headers_admin)
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)

    def test_delete_user_fail(self):
        res = self.client().delete('/user/1000', headers=self.headers_admin)
        data = json.loads(res.data)
        self.assertEqual(data['message'], 'User does not exist')

    def test_post_book(self):
        res = self.client().post(
            '/books',
            headers=self.headers_reader,
            json={
                "title": "Ikigai",
                "author": "Hector Gracia",
                "user_id": 3
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_books(self):
        res = self.client().get(
            '/books',
            headers=self.headers_reader)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_book_fail(self):
        res = self.client().post(
            '/books',
            headers=self.headers_reader,
            json={
                "title": "Ikigai",
                "author": "Hector Gracia",
                "user_id": 1000
            })
        data = json.loads(res.data)
        self.assertEqual(data['message'], 'provided user does not exist')

    def test_post_request(self):
        res = self.client().post(
            '/request/2',   # TODO specify existing user id in URL to make test return OK
            headers=self.headers_reader,
            json={
                "lender_id": 1,     # TODO specify book owner id for below book id
                "book_id": 1       # TODO specify book id
            })
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)

    def test_post_request_fail(self):
        res = self.client().post(
            '/request/5',
            headers=self.headers_reader,
            json={
                "lender_id": 3
            })
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)

    def test_get_user_requests_fail(self):
        res = self.client().get(
            '/requests/1000')
        data = json.loads(res.data)
        self.assertEqual(data['message'], 'User does not exist')

    def test_get_user_requests(self):
        res = self.client().get(
            '/requests/3')   # TODO specify user id(for whom there exists a request) in URL to make test return OK
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)

    def test_post_patch_request(self):
        res = self.client().patch(
            '/requests/3')      # TODO specify user id(for whom there exists a request) in URL to make test return OK
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)

    def test_post_patch_request_fail(self):
        res = self.client().patch(
            '/requests/10')
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)


if __name__ == "__main__":
    unittest.main()
