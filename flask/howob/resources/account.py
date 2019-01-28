from flask_restful import reqparse, abort, Resource
from ast import literal_eval
from flask import jsonify, json
from uuid import uuid4
from db import db

parser = reqparse.RequestParser()
parser.add_argument('account_key', help='Error: {error_msg}')
parser.add_argument('account_pseudo', help='Error: {error_msg}')
parser.add_argument('account_pass', help='Error: {error_msg}')
parser.add_argument('account_characters',
                    help='Error: {error_msg}', action='append')
parser.add_argument('account_hash_type', help='Error: {error_msg}')
parser.add_argument('account_email', help='Error: {error_msg}')
parser.add_argument('rts_account_key', help='Error: {error_msg}')


"""
account: hash {
  account_key: {
      account_pseudo: string
      account_pass: hash
      account_characters: [
        {
          character_key: UUID
          character_name: string
          character_level: int
          class_name: string
          class_key: UUID
        }
      ]
      account_hash_type: string
      account_email: string
      account_adress: string
      (distibuted services variables)
    }
}
"""


class Account(Resource):

    def get(self, UUID):
        checkUUID(UUID)
        data = json.loads(db.hget('accounts', UUID))
        response = dict()
        response["account_characters"] = data["account_characters"]
        response["account_key"] = UUID
        # print(response)
        return response

    def post(self):
        args = parser.parse_args()
        if db.hexists('accounts_search', args.account_pseudo) != 0 or db.hexists('accounts_search', args.account_email) != 0:
            abort(403, message="account name or email already in database")
        UUID = str(uuid4())
        # print(UUID)
        args.account_characters = []
        args.account_key = UUID
        args.rts_account_key = "not yet linked"
        account = json.dumps(args)
        data = {UUID: account}
        # print(data)
        # print(type(data))
        db.hmset('accounts', data)
        db.hset('accounts_search', args.account_pseudo, UUID)
        db.hset('accounts_search', args.account_email, UUID)
        return UUID, 200

    def delete(self, UUID):
        checkUUID(UUID)
        db.hdel('accounts', UUID)
        return "ok", 204

    def put(self, UUID):
        args = parser.parse_args()
        checkUUID(UUID)
        account = json.dumps(args)
        data = {UUID: account}
        db.hmset('accounts', data)
        return "ok", 204


def checkUUID(UUID):
    # print(db.hget('accounts', UUID))
    if not db.hexists('accounts', UUID):
        abort(404, message="UUID {} doesn't exist".format(UUID))
    return True
