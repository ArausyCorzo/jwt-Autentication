"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('FLASK_APP_KEY')
jwt = JWTManager(app)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_get_user():
    response = []
    users = User.query.all()
    if users:
        for user in users:
            response.append(user.serialize())
        return jsonify(response), 200
    else:
        return([]), 500

@app.route('/signup', methods=['POST'])    
def handle_signup():
    body = request.json
    new_user = User.create_user(body)
    if new_user is not None:
        return jsonify(new_user.serialize()), 201
    else:
        return jsonify({"message": "oops, could not create user :(, please try again"}), 500

@app.route('/login', methods=['POST'])
def handle_signin():
    email = request.json["email"]
    password = request.json["password"]
    user = User.query.filter_by(email = email, password = password).one_or_none()
    if user is not None:
        token = create_access_token(identity = user.id)
        return jsonify({"token": token, "user_id": user.id}), 200
    else:
        return ({"message": "oops, bad credentials, please try again"}), 401    
           
# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
