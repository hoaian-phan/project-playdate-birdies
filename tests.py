import unittest

from server import app
from model import db, example_data, connect_to_db
from passlib.hash import argon2
import json


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
        self.assertNotIn(b"Log In", result.data)

    def test_login_page(self):
        """ Test the log in page """
        result = self.client.get("/login")
        self.assertIn(b"Log In", result.data)
        self.assertNotIn(b"Create your account", result.data)

    def test_no_hosting_without_login(self):
        """ Test that the hosting page can't open if user is not logged in """
        result = self.client.get("/host", follow_redirects=True)
        self.assertNotIn(b"Host a Playdate", result.data)
        self.assertIn(b"Log In", result.data)
        self.assertIn(b"Please log in to host a playdate", result.data)

    def test_no_register_without_login(self):
        """ Test that the attend page won't open if user is not logged in """
        result = self.client.get("/attend", follow_redirects=True)
        self.assertNotIn(b"Tell us about you", result.data)
        self.assertIn(b"Log In", result.data)
        self.assertIn(b"Please log in to register", result.data)


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
        self.assertIn(b"welcome to Playdate Birdies community", result.data)
        self.assertIn(b"Where Kids Play, Grow and Make Friends", result.data)

    def test_login_form(self):
        """ Test the log in form"""

        self.client.post("/signup", data={"email": "nunu@hb.com", "password": "12345",
                                                    "confirm_password": "12345",
                                                    "first": "Nunu", "last": "Phan"})
        result = self.client.post("/login", data={"email": "nunu@hb.com", "password": "12345"},
                                  follow_redirects=True)
        
        self.assertNotIn(b"Log In", result.data)
        self.assertIn(b"Where Kids Play, Grow and Make Friends", result.data)

    def test_logout_page(self):
        """ Test the logout feature """

        self.client.post("/signup", data={"email": "nunu@hb.com", "password": "12345",
                                                    "confirm_password": "12345",
                                                    "first": "Nunu", "last": "Phan"})
        self.client.post("/login", data={"email": "nunu@hb.com", "password": "12345"},
                                  follow_redirects=True)
        result = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"You were logged out.", result.data)
        self.assertIn(b"Where Kids Play, Grow and Make Friends", result.data)

    def test_hosting_with_login(self):
        """ Test the user can only host after logging in """

        self.client.post("/signup", data={"email": "nunu@hb.com", "password": "12345",
                                                    "confirm_password": "12345",
                                                    "first": "Nunu", "last": "Phan"})
        self.client.post("/login", data={"email": "nunu@hb.com", "password": "12345"},
                                  follow_redirects=True)
        result = self.client.get("/host", follow_redirects=True)
        self.assertIn(b"Host a Playdate", result.data)
        self.assertNotIn(b"Where Kids Play, Grow and Make Friends", result.data)

    def test_host_a_playdate(self):
        """ Test user can host a playdate """

        self.client.post("/signup", data={"email": "nunu@hb.com", "password": "12345",
                                                    "confirm_password": "12345",
                                                    "first": "Nunu", "last": "Phan"})
        self.client.post("/login", data={"email": "nunu@hb.com", "password": "12345"},
                                  follow_redirects=True)
        result = self.client.post("/host", data={"title": "playdate of", "description": 'Have fun and make friends', "location": "Greenwood Park", 
                                                "address": "24016 Eden Ave", "city": "Hayward", "zipcode": "94541", "state": "CA",
                                                "date": "2022-04-10", "start": '11:00:00', "end": '15:00:00', "age_group": "any age"},
                                            follow_redirects=True)                               
        self.assertIn(b"Congratulations! You will be an awesome host!", result.data)
        self.assertIn(b"Contact info", result.data)

    def test_search_a_playdate(self):
        """ Test user can search for a playdate """

        self.client.post("/signup", data={"email": "nunu@hb.com", "password": "12345",
                                                    "confirm_password": "12345",
                                                    "first": "Nunu", "last": "Phan"})
        result = self.client.get("/search", data={"city_zipcode": "94541", "date": "2022-04-10", "age_group": "any age"}, 
                                            follow_redirects=True)                               
        self.assertIn(b"result for your search", result.data)
        self.assertNotIn(b"Where Kids Play, Grow and Make Friends", result.data)


if __name__ == "__main__":
    unittest.main()