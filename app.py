import os
import json
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Actors, Movies
from auth import AuthError, requires_auth


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config['TESTING']=False
    CORS(app)
    setup_db(app)

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,POST,DELETE,PATCH')
        return response

    # ROUTES
    '''
        GET index
            just a simple health check
    '''


    @APP.route('/')
    def health_check():
        msg = "Welcome to CRH-FSND-Casting"
        return jsonify(msg)


'''
    GET /movies
        get all movies
'''


@APP.route('/movies')
@requires_auth('get:movies')
def get_movies(something):
    try:
        movies = Movie.query.all()
        return jsonify({"success": True, "movies": movies})
    except Exception as e:
        print(e)
        abort(422)


'''
    GET /movies/id
        get specific movie by id
        @TODO: add auth get:movies
'''


@APP.route('/movies/<int:movie_id>')
@requires_auth('get:movies')
def get_movie_by_id(something, movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        abort(404)
    else:
        return jsonify({"success": True, "movies": movie})


'''
    POST /movies/new
        create a new movie entry
'''


@APP.route('/movies/new', methods=['POST'])
@requires_auth('post:movies')
def add_new_movie(something):
    try:
        data = json.loads(request.data)
        print(data)
    except Exception as e:
        print(e)
        abort(400)
    try:
        entry = MovieSchema.from_dict(data)
        entry_dict = asdict(entry)
        movie = Movie(title=entry_dict['title'],
                      requirements=json.dumps(entry_dict['requirements']),
                      release_date=entry_dict['release_date'])
        print(movie)
        movie.insert()
        return jsonify({"success": True})
    except Exception as e:
        return formatted_json_validation_error(e)


'''
    PATCH /movies/id
        edit a movie entry with id
'''


@APP.route('/movies/<int:movie_id>', methods=['PATCH'])
@requires_auth('patch:movies')
def patch_movie(something, movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        abort(404)

    try:
        data = json.loads(request.data)
    except Exception as e:
        print(e)
        abort(400)

    try:
        # @TODO: find an implementationthat does rigorous checks like post
        if 'title' in data:
            movie.title = data['title']
        if 'release_date' in data:
            movie.release_date = data['release_date']
        if 'requirements' in data:
            if MovieRequirements.from_dict(data['requirements']):
                movie.requirements = data['requirements']
        movie.update()
        return jsonify({"success": True, "movie": movie})
    except Exception as e:
        print(e)
        return formatted_json_validation_error(e)


'''
    DELETE /movies/id
        delete a movie entry with id
'''


@APP.route('/movies/<int:movie_id>', methods=['DELETE'])
@requires_auth('delete:movies')
def delete_movie(something, movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        abort(404)
    try:
        print("Request to delete Movie #", movie_id)
        movie.delete()
        return jsonify({"success": True, "movie": movie})
    except Exception as e:
        print(e)
        abort(422)


'''
    GET /actors
        get all actors
'''


@APP.route('/actors')
@requires_auth('get:actors')
def get_actors(something):
    try:
        actors = Actor.query.all()
        return jsonify({"success": True, "actors": actors})
    except Exception as e:
        print(e)
        abort(422)


'''
    GET /actors/id
        get specific actor by id
'''


@APP.route('/actors/<int:actor_id>')
@requires_auth('get:actors')
def get_actor_by_id(something, actor_id):
    actor = Actor.query.get(actor_id)
    if not actor:
        abort(404)
    else:
        return jsonify({"success": True, "actors": actor})


'''
    POST /actors/new
        create a new actor entry
'''


@APP.route('/actors/new', methods=['POST'])
@requires_auth('post:actors')
def add_new_actor(something):
    try:
        data = json.loads(request.data)
        print(data)
    except Exception as e:
        print(e)
        abort(400)
    try:
        entry = ActorSchema.from_dict(data)
        entry_dict = asdict(entry)
        actor = Actor(name=entry_dict['name'],
                      age=entry_dict['age'],
                      gender=entry_dict['gender'])
        print(actor)
        actor.insert()
        return jsonify({"success": True})
    except Exception as e:
        return formatted_json_validation_error(e)


'''
    PATCH /actors/id
        edit an actor entry with id
'''


@APP.route('/actors/<int:actor_id>', methods=['PATCH'])
@requires_auth('patch:actors')
def patch_actor(something, actor_id):
    actor = Actor.query.get(actor_id)
    if not actor:
        abort(404)

    try:
        data = json.loads(request.data)
    except Exception as e:
        print(e)
        abort(400)

    try:
        # @TODO: find an implementation that does rigorous checks like post
        if 'name' in data:
            actor.name = data['name']
        if 'age' in data:
            actor.age = data['age']
        if 'gender' in data:
            actor.gender = data['gender']
        actor.update()
        return jsonify({"success": True, "actor": actor})
    except Exception as e:
        print(e)
        abort(422)


'''
    DELETE /actors/id
        delete an actor entry with id
'''


@APP.route('/actors/<int:actor_id>', methods=['DELETE'])
@requires_auth('delete:actors')
def delete_actor(something, actor_id):
    actor = Actor.query.get(actor_id)
    if not actor:
        abort(404)
    try:
        print("Request to delete Actor #", actor_id)
        actor.delete()
        return jsonify({"success": True, "actor": actor})
    except Exception as e:
        abort(422)


# Error Handling

@APP.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
    Error handler for 404
'''


@APP.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not Found"
    }), 404


'''
    Error handler for 400
'''


@APP.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Your request was not a correct json"
    }), 400


'''
    Error handler for AuthError
'''

@APP.errorhandler(AuthError)
def autherror(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code

return app


app = create_app()


if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=False)
