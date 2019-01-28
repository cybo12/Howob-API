from flask_restful import reqparse, abort, Resource
from ast import literal_eval
from flask import jsonify, json, make_response, request
from uuid import uuid4
from db import db
from functools import wraps
import logging
from server_communication import communication_core

parser = reqparse.RequestParser()
parser.add_argument('account_login', help='Error: {error_msg}')
parser.add_argument('account_hash', help='Error: {error_msg}')
parser.add_argument('rts_account_key', help='Error: {error_msg}')


"""
account: hash {
  account_key: {
      account_login: string
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


class Authentication(Resource):

    def post(self):
        # print("no processed data receive : {}".format(request.data))
        args = parser.parse_args()
        args.account_hash = args.account_hash.upper()
        checkPseudoHash(args.account_login, args.account_hash)
        account = checkAuth(args.account_login, args.account_hash)
        account.pop("account_characters")
        return account

    def put(self):
        logging.info("patch auth RTS")
        logging.info("no processed data receive : {}".format(request.data))
        args = parser.parse_args()
        args.account_hash = args.account_hash.upper()
        checkPseudo(args.account_login)
        account = checkAuth(args.account_login, args.account_hash, False)
        if(db.hexists('accounts_search', account["rts_account_key"])):
            db.hdel('accounts_search', account["rts_account_key"])
        account["rts_account_key"] = args.rts_account_key
        logging.info("change for {}".format(account))
        db.hset('accounts_search', args.rts_account_key,
                account["account_key"])
        db.hset('accounts', account["account_key"], json.dumps(account))
        # test = str(request.__dict__)
        # res = make_response(test, 200)
        return 'modified', 200


def checkAuth(account_login, account_hash):
    response = False
    search = db.hget('accounts_search', account_login)
    account = db.hget('accounts', search)
    account = json.loads(account)
    if 'account_pass' in account:
        if account['account_pass'] == account_hash:
            response = account
        else:
            abort(401, message="incorrect password")
    else:
        if communication_core.auth_RTS(account_login, account_hash):
            response = account
        else:
            abort(401, message="incorrect password for RTS auth")
    return response


def checkPseudo(pseudo):
    # print(db.hget('accounts', UUID))
    if not db.hexists('accounts_search', pseudo):
        abort(404, message="Pseudo or email {} doesn't exist".format(pseudo))
    return True


def checkPseudoHash(pseudo, account_hash):
    # print(db.hget('accounts', UUID))
    response = True
    if not db.hexists('accounts_search', pseudo):
        if not(communication_core.auth_RTS(pseudo, account_hash)):
            response = False
            abort(404, message="Pseudo or email {} doesn't exist".format(pseudo))
    return response
