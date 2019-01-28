from flask_restful import reqparse, abort, Resource
from ast import literal_eval
from flask import jsonify, json
from uuid import uuid4
from db import db
import random
import string
from datetime import datetime
from server_communication import communication_core

parser = reqparse.RequestParser()
parser.add_argument('message', help='Error: {error_msg}')


class Social(Resource):

    def post(self):
        response = True
        args = parser.parse_args()
        response = communication_core.post_twitter(
            "#" + randomString(4) + ": " + args.message)
        return response, 200

    def get(self):
        return "coucou"


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
