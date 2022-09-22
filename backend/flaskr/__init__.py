import os
import re
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
CATEGORY = "category"
QUESTION = "question"

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*" : {'origins': '*'}})

    # Customer function to format categorie
    def format_json(categories):
    
        formatCategory = dict()

        for category in categories:
            formatCategory.update({
                category.id: category.type
            })

        return formatCategory
        
        
    def paginate_questions(request, questions):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        current_questions = [question.format() for question in questions]

        return current_questions[start:end]

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        """add in response header Acces-Control-Allow for all requests """
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')

        return response

    #ENDPOINTS
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        """
        GET /categories
        curl http://127.0.0.1:5000/categories
        """
        try:
            categories = Category.query.all()
            print(categories)
            if len(categories) == 0:
                abort(404)

            formatted_categories = format_json(categories)
            return jsonify({
                'success': True,
                'categories': formatted_categories,
                'total_categories': len(categories)
            })
        except:
            abort(500)


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        """
        GET /questions
        Sample: curl http://127.0.0.1:5000/questions
        """
        try:
            questions = Question.query.order_by(Question.id).all()

            paginate = paginate_questions(request, questions)
            if len(paginate) == 0:
                abort(404)

            categories = Category.query.order_by(Category.id).all()
            formatted_categories = format_json(categories)

            return jsonify({
                'success': True,
                'questions': paginate,
                'total_questions': len(questions),
                'current_category': None,
                'categories': formatted_categories
            }), 200
        except:
            abort(500)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """
        DELETE /question/{question_id}
        curl http://127.0.0.1:5000/questions/3 -X DELETE
        """
        try:
            question = Question.query.get(question_id) 
            if question is None:
                abort(404)

            question.delete()
        except:
            abort(500)

        return jsonify({
            'success': True,
            'total_question': len(Question.query.all())
        }), 200

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def new_question():
        """
        POST /question
        curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{
            "question": "How many student are fullstack dev?",
            "answer": "20",
            "difficulty": 3,
            "category": "5"
            }'
        """
        
        data = request.get_json()
        question = data.get('question', '')
        answer = data.get('answer', '')
        category = data.get('category', '')
        difficulty = data.get('difficulty', '')
        if len(question) == 0 or len(answer) == 0:
            abort(400)
        # check if question is already exist
        question_list = Question.query.all()
        questions_exist = [q.format()['question']
                              for q in question_list]
        if question in questions_exist:
            abort(422)

        new_question_id = None

        try:
            new_question = Question(
                question,
                answer,
                category,
                difficulty
            )
            new_question.insert()
            new_question_id = new_question.id

        except:
            abort(500)

        return jsonify({
            'success': True,
            'total_questions': len(Question.query.all()),
            'question_id': new_question_id
        }), 201

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/search', methods=['POST'])
    def search_question():
        """
        POST /search
        curl http://127.0.0.1:5000/search -X POST -H "Content-Type: application/json" -d '{
        "searchTerm": "usa"
        }'
        """
        try:
            data = request.get_json()
            search_term = data.get('searchTerm', '')
            if len(search_term) == 0:
                abort(404)

            questions = Question.query.order_by(Question.id).filter(
                Question.question.ilike(f'%{search_term}%')).all()
            if len(questions) == 0:
                abort(404)
            format_questions = paginate_questions(request, questions)

            categories = Category.query.order_by(Category.id).all()
            format_categories = format_json(categories)
        except:
            abort(500)

        return jsonify({
            'success': True,
            'questions': format_questions,
            'total_questions': len(questions),
            'categories': format_categories,
            'current_categroy': None
        }), 201

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=["GET"])
    def get_questions_by_category(category_id):
        """
        GET /categories/{category_id}/questions
        curl http://127.0.0.1:5000/categories/5/questions
        """
        try:
            category = Category.query.get(category_id).type

            questions = Question.query.order_by(Question.id).filter(
                Question.category == str(category_id)).all()
            if len(questions) == 0:
                abort(404)

            format_question = paginate_questions(request, questions)
        except:
            abort(500)

        return jsonify({
            'success': True,
            'questions': format_question,
            'current_category': category,
            'total_questions': len(questions)
        }), 200

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_random_question():
        """
        POST /quizzes
        curl http://127.0.0.1:5000/quizzes -X POST -H "Content-Type: application/json" -d '{
            "previous_questions": [11],
            "quiz_category": {
                "type": "Art",
                "id": "2"
                }
            }'
        """
        data = request.get_json()
        previous_questions = data.get('previous_questions', '')
        category = data.get('quiz_category', '')

        if previous_questions == '' or category == '':
            abort(400)
        
        
        questions = Question.query.all() if category['id'] == 0 else Question.query.filter(Question.category == category['id']).all()

        if len(questions) == 0:
            abort(404)
            
        question = None
        print("_____________________previous-question_________________________")
        print(previous_questions)
        print(questions)
        while True:
    
            if len(previous_questions) == len(questions):
                return jsonify({
                    'success': True
                }), 201

            question = questions[random.randint(0, len(questions) - 1)]
            if question.id not in previous_questions:
                break
            

        return jsonify({
            'success': True,
            'question': question.format()
        }), 201


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    
    # ERRORS

    @app.errorhandler(400)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request',
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable'
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
        }), 500

        
    return app

