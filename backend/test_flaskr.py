import os
from sre_constants import SUCCESS
from unicodedata import category
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_PATH_TEST


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = DB_PATH_TEST
        setup_db(self.app, self.database_path)

        self.test_question = {
            'answer': 'laye',
            'difficulty': 5,
            'category': '4',
            'question': 'Who is the first usa president'          
        }
        self.test_question_add = {
            'answer': 'false',
            'difficulty': 1,
            'category': '5',
            'question': 'all fullstack dev are fates'          
        }
        self.test_search_term = {
            'searchTerm': self.test_question_add['question'].split(' ')[2]          
        }
        self.test_quizz = {
            'previous_questions': [10],
            'quiz_category': {
                'type': 'Sports',
                'id': '6'
            }
        }

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

    # PAGINATION
    def test_paginate_questions(self):
        question_response = self.client().get('/questions')
        datas = json.loads(question_response.data)

        self.assertEqual(datas['success'], True)
        self.assertEqual(question_response.status_code, 200)

        self.assertTrue(len(datas['questions']))
        self.assertTrue(datas['total_questions'])

    def test_paginate_questions_fail(self):
        question_response = self.client().get('/questions?page=900')
        datas = json.loads(question_response.data)

        self.assertEqual(question_response.status_code, 404)
        self.assertEqual(datas['success'], False)
        self.assertEqual(datas['message'], 'Resource not found')

    
    # GET /categories
    def test_get_categories(self):
        category_response = self.client().get('/categories')
        datas = json.loads(category_response.data)

        self.assertEqual(datas['success'], True)
        self.assertEqual(category_response.status_code, 200)
    
    def test_get_categories_fail(self):
        category_response = self.client().get('/categories')
        datas = json.loads(category_response.data)

        self.assertEqual(len(datas), 0)
        self.assertEqual(category_response.status_code, 404)
        self.assertEqual(datas['success'], False)
        self.assertEqual(datas['message'], 'Resource not found')


    # GET /questions
    def test_get_questions(self):
        question_response = self.client().get('/questions')
        datas = json.loads(question_response.data)

        self.assertEqual(datas['success'], True)
        self.assertEqual(question_response.status_code, 200)
    
    def test_get_questions_fail(self):
        question_response = self.client().get('/questions')
        datas = json.loads(question_response.data)

        self.assertEqual(len(datas), 0)
        self.assertEqual(question_response.status_code, 404)
        self.assertEqual(datas['success'], False)
        self.assertEqual(datas['message'], 'Resource not found')


    # DELETE /questions/{question_id}
    def test_delete_questions(self):
        new_question_test = Question(
            question=self.test_question['question'],
            answer=self.test_question['answer'],
            category=self.test_question['category'],
            difficulty=self.test_question['difficulty']
        )
        new_question_test.insert()
        new_question_test_id = new_question_test.id
        question_response = self.client().delete(f'/questions/{new_question_test_id}')
        datas = json.loads(question_response.data)

        self.assertEqual(datas['success'], True)
        self.assertEqual(question_response.status_code, 200)
    
    def test_delete_questions_fail(self):
        question_response = self.client().delete('/questions/200000')
        datas = json.loads(question_response.data)

        self.assertEqual(question_response.status_code, 404)
        self.assertEqual(datas['success'], False)
        self.assertEqual(datas['message'], 'Resource not found')
        

    # POST /questions
    def test_post_questions(self):
        question_response = self.client().post('/questions', json=self.test_question_add)
        datas = json.loads(question_response.data)

        self.assertTrue(len(self.test_question_add['question']) > 0 and len(self.test_question_add['answer']) > 0)
        questions = Question.query.all()
        self.assertTrue(self.test_question_add['question'] != question.format()['question'] for question in questions)

        self.assertEqual(datas['success'], True)
        self.assertEqual(question_response.status_code, 201)
        new_question_test_delete = datas['question_id']

        # DELETE new question always for the next test
        self.client().delete(f'/questions/{new_question_test_delete}')
    
    def test_post_questions_fail(self):
        question_response = self.client().post('/questions', json=dict())
        datas = json.loads(question_response.data)

        self.assertTrue(len(self.test_question_add['question']) > 0 and len(self.test_question_add['answer']) > 0)

        self.assertEqual(question_response.status_code, 404)
        self.assertEqual(datas['success'], False)
        self.assertEqual(datas['message'], 'Resource not found')


    # POST /search
    def test_search_questions(self):
        # add new question to delete after search 
        new_question_response = self.client().post('/questions', json=self.test_question_add)
        new_question_datas = json.loads(new_question_response.data)
        new_question_test_delete = new_question_datas['question_id']

        # make search
        question_response = self.client().post('/search', json=self.test_search_term)
        datas = json.loads(question_response.data)

        self.assertEqual(datas['success'], True)
        self.assertEqual(question_response.status_code, 201)

        # DELETE new question always for the next test
        self.client().delete(f'/questions/{new_question_test_delete}')
    
    def test_search_questions_fail(self):
        question_response = self.client().post('/search', json=dict())
        datas = json.loads(question_response.data)

        self.assertTrue(len(datas) > 0)

        self.assertEqual(question_response.status_code, 404)
        self.assertEqual(datas['success'], False)
        self.assertEqual(datas['message'], 'Resource not found')


    # GET /categories/{category_id}/questions
    def test_get_questions_by_category(self):
        question_response = self.client().get('categories/2/questions')
        datas = json.loads(question_response.data)

        self.assertEqual(datas['success'], True)
        self.assertEqual(question_response.status_code, 201)
    
    def test_get_questions_by_category_fail(self):
        question_response = self.client().get('categories/100/questions')
        datas = json.loads(question_response.data)

        self.assertEqual(question_response.status_code, 404)
        self.assertEqual(datas['success'], False)
        self.assertEqual(datas['message'], 'Resource not found')

    
    # POST /quizzes
    def test_get_random_question(self):
        question_response = self.client().post('/quizzes', json=self.test_quizz)
        datas = json.loads(question_response.data)

        self.assertEqual(datas['success'], True)
        self.assertEqual(question_response.status_code, 201)
    
    def test_get_random_question_fail(self):
        question_response = self.client().post('/quizzes', json=dict())
        datas = json.loads(question_response.data)

        self.assertEqual(question_response.status_code, 404)
        self.assertEqual(datas['success'], False)
        self.assertEqual(datas['message'], 'Resource not found')

   


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
