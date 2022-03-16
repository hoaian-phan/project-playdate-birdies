import unittest

from server import app
from model import db, example_data, connect_to_db

class PlayDateTest(unittest.TestCase):
    """ Test for the sign up feature"""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_homepage(self):
        """ Test the homepage """
        result = self.client.get("/")
        self.assertIn(b"Where Kids Play, Grow and Make Friends", result.data)

    def test_signup_page(self):
        """ Test the sign up page """
        result = self.client.get("/signup")
        self.assertIn(b"Create your account", result.data)

    def test_login_page(self):
        """ Test the log in page """
        result = self.client.get("/login")
        self.assertIn(b"Log In", result.data)


class PlayDateDatabase(unittest.TestCase):
    """ Flask tests that use the database"""

    def setUp(self):
        """ To do before every test"""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database 
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data 
        db.create_all()
        example_data()


    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_signup_form(self):
        """ Test the sign up form"""
        result = self.client.post("/signup", data={"email": "hoaian@hb.com", "password": "12345",
                                                    "confirm_password": "12345",
                                                    "first": "Hoaian", "last": "Phan"},
                                            follow_redirects=True)
        self.assertNotIn(b"Create an account", result.data)
        self.assertIn(b"Successfully created an account", result.data)
        self.assertIn(b"Where Kids Play, Grow and Make Friends", result.data)

    def test_login_form(self):
        """ Test the log in form"""
        result = self.client.post("/login", data={"email": "nu@hb.com", "password": "12345"},
                                  follow_redirects=True)
        self.assertIn(b"Log in successfully.", result.data)
        self.assertNotIn(b"Log In", result.data)
        self.assertIn(b"Where Kids Play, Grow and Make Friends", result.data)


if __name__ == "__main__":
    unittest.main()