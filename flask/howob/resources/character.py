from flask_restful import reqparse, abort, Resource
from ast import literal_eval
from flask import jsonify, json, make_response
from uuid import uuid4
from db import db

parser = reqparse.RequestParser()
parser.add_argument('account_key', help='Error: {error_msg}')
parser.add_argument('character_level', type=int, help='Error: {error_msg}')
parser.add_argument('character_experience', type=int,
                    help='Error: {error_msg}')
parser.add_argument('character_max_life', type=int, help='Error: {error_msg}')
parser.add_argument('character_life', type=int, help='Error: {error_msg}')
parser.add_argument('character_max_mana', type=int, help='Error: {error_msg}')
parser.add_argument('character_mana', type=int, help='Error: {error_msg}')
parser.add_argument('class_key', type=int, help='Error: {error_msg}')
parser.add_argument('character_type_key', type=int, help='Error: {error_msg}')
parser.add_argument('character_last_position', help='Error: {error_msg}')
parser.add_argument('character_nb_quests', type=int, help='Error: {error_msg}')
parser.add_argument('character_nb_gold', type=int, help='Error: {error_msg}')
parser.add_argument('character_name', help='Error: {error_msg}')

"""
{
character_name: string
    character_key: UUID
    character_level: int
    character_experience: long
    character_life: int
    character_max_life: int
    character_mana: int
    character_max_mana: int
    class_key: UUID
    character_type_key: UUID
    character_last_position: {
      x: int
      y: int
    }
    character_nb_quests: int
    character_nb_gold: int
  }

"""
keep_informations = ['account_key',
                     'character_name', 'class_key', 'character_level']


class Character(Resource):

    def get(self, UUID=None):
        if not UUID:
            responses = db.hgetall('characters')
            traited_responses = {}
            for key, value in responses.items():
                dict_temp = literal_eval(responses[key])
                dict_temp['character_last_position'] = literal_eval(
                    dict_temp['character_last_position'])
                responses[key] = dict_temp
                if dict_temp['account_key'] == 0:
                    traited_responses[key] = responses[key]
        else:
            checkUUID(UUID, 'characters')
            response = db.hget('characters', UUID)
            response = literal_eval(response)
            response["character_last_position"] = literal_eval(
                response.get("character_last_position"))
            response["character_key"] = UUID
            traited_responses = response
        return traited_responses

    def post(self):
        args = parser.parse_args()
        UUID = str(uuid4())
        if not args.account_key:
            args.account_key = 0
        if len(args.account_key) < 5:
            args.account_key = 0
        character_to_add = dict(args)
        # print(UUID)
        # print(character_to_add)
        if args.account_key is not 0:
            if checkUUID(args.account_key, 'accounts'):
                account = literal_eval(db.hget('accounts', args.account_key))
                temp = dict()
                for information in character_to_add:
                    if information in keep_informations:
                        temp[information] = character_to_add[information]
                temp['class_name'] = literal_eval(db.hget('classes', temp["class_key"]))['class_name']
                temp['character_key'] = UUID
                account["account_characters"].append(temp)
                # print(temp)
                # print(account["account_characters"])
                data_account = {args.account_key: json.dumps(account)}
                db.hmset('accounts', data_account)
                db.hset('quests', UUID, "{}")
            else:
                abort(404, message="uuid {} not found".format(args.account_key))
        data = {UUID: json.dumps(character_to_add)}
        db.hmset('characters', data)
        # print(UUID)
        return UUID, 200

    def delete(self, UUID):
        checkUUID(UUID, 'characters')
        db.hdel('characters', UUID)
        return make_response('', 204)

    def put(self, UUID):
        args = parser.parse_args()
        checkUUID(UUID, 'characters')
        args.character_key = UUID
        character = json.dumps(args)
        data = {UUID: character}
        db.hmset('characters', data)
        return make_response('', 204)


def checkUUID(UUID, target):
    # print(db.hget('characters', UUID)
    if not db.hexists(target, UUID):
        abort(404, message="UUID {} doesn't exist".format(UUID))
    return True
