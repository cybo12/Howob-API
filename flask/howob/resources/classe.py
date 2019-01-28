from flask_restful import reqparse, abort, Resource
from ast import literal_eval
from flask import jsonify, json
from uuid import uuid4
from db import db
import logging

parser = reqparse.RequestParser()
parser.add_argument('class_key', help='Error: {error_msg}')
parser.add_argument('class_name', help='Error: {error_msg}')
parser.add_argument('class_attacks',
                    help='Error: {error_msg}', action='append')
parser.add_argument('character_defaults', help='Error: {error_msg}')

"""
classes: hash {
  class_key:  {
    class_key: UUID
    class_name: string
    class_attacks: [
      {
        attack_key: UUID
        attack_name: string
        attack_description: string
        attack_damage: string
      }
    ]
    character_defaults: {
      character_max_life: int
      character_max_mana: int
    }
  }
}
"""


class Classe(Resource):

    def get(self, UUID=None):
        if UUID:
            if int(UUID) == 99:
                data = dict(db.hgetall('classes'))
                response = dict()
                for key in data:
                    if(int(key) < 5):
                        response[key] = json.loads(data[str(key)])
            else:
                checkUUID(UUID)
                response = literal_eval(db.hget('classes', UUID))['class_attacks']
        else:
            response = dict(db.hgetall('classes'))
            for key in response:
                response[key] = json.loads(response[key])
            # print(response)
        return jsonify(response)

    def post(self):
        args = parser.parse_args()
        if args.class_attacks != {}:
            attacks = {}
            for attack in args.class_attacks:
                attacks[str(uuid4())] = literal_eval(attack)
            args.class_attacks = attacks
        args.character_defaults = literal_eval(args.character_defaults)
        # print(new)
        data = {args.class_key: json.dumps(args)}
        # print(data)
        db.hmset('classes', data)
        return args.class_key, 200


def checkUUID(UUID):
    # print(db.hget('classe', UUID))
    if not db.hexists('classes', UUID):
        abort(404, message="UUID {} doesn't exist".format(UUID))
    return True
