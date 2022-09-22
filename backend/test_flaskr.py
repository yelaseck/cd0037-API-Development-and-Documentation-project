import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_username = 'laye'
        self.database_password = 'laye'
        self.database_path = "postgres://{}:{}@{}/{}".format(self.database_username, self.database_password, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_paginate_questions(self):
        """Tests success of question pagination"""

        # get response and load data
        response = self.client().get('/questions')
        datas = json.loads(response.data)

        # check status code and message
        self.assertEqual(datas['success'], True)
        self.assertEqual(response.status_code, 200)

        # check questions and total_questions return data
        self.assertTrue(len(datas['questions']))
        self.assertTrue(datas['total_questions'])

    def test_paginate_question_fails_404(self):
        """Test fail 404 question pagination"""

        # send request with bad page data and load response
        response = self.client().get('/questions?page=900')
        data = json.loads(response.data)

        # check status code, success and message value.
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
