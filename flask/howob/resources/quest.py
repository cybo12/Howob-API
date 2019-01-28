from flask_restful import reqparse, abort, Resource
from ast import literal_eval
from flask import jsonify, json, request
from uuid import uuid4
from db import db
import logging

parser = reqparse.RequestParser()
parser.add_argument('character_key', help='Error: {error_msg}')
parser.add_argument('list', action='append', help='Error: {error_msg}')
parser.add_argument('quest_key', help='Error: {error_msg}')

"""
quest: hash {
    character_key: [
        {
          quest_key: UUID
          quest_name: string
          quest_description: string
          quest_gold: int
          quest_experience: int
          quest_type_key: UUID
          quest_advancement: {
            variable according to type
          }
        }
      ]
}
"""


class Quest(Resource):

    def get(self, UUID=None):
        if not UUID:
            responses = db.hgetall('quests')
            traited_responses = {}
            for key, value in responses.items():
                if db.hexists('accounts', key) == 0:
                    traited_responses[key] = literal_eval(responses[key])
        else:
            checkUUID(UUID)
            traited_responses = literal_eval(db.hget('quests', UUID))
        # print(traited_responses)
        return traited_responses, 200

    def post(self):
        args = parser.parse_args()
        # print(args.list)
        quests = {}
        for quest in args.list:
            UUID = str(uuid4())
            quests[UUID] = dict(literal_eval(quest))
        # print(quests)
        quests = json.dumps(quests)
        data = {args.character_key: quests}
        db.hmset('quests', data)
        return args.character_key, 200

    def delete(self, UUID):
        checkUUID(UUID)
        db.hdel('quests', UUID)
        return "", 204

    def put(self, UUID):
        checkUUID(UUID)
        # logging.info(f" data put quest not processed :{request.data}")
        update = json.loads(request.data.decode('utf8'))
        # logging.info(f"put de quest: {update}")
        # logging.info(f"put de quest: {type(update)}")
        replace = {UUID: json.dumps(update)}
        # print(f"ce qu'on replace : {replace}")
        db.hmset('quests', replace)
        return "", 204


def checkUUID(UUID):
    # print(db.hget('quest', UUID))
    if not db.hexists('quests', UUID):
        abort(404, message="UUID {} doesn't exist".format(UUID))
    return True
