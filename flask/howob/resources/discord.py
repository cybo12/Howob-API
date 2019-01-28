from flask_restful import reqparse, abort, Resource
from ast import literal_eval
from flask import jsonify, json
from db import db

no_keep_information = ['account_key', 'character_key',
                       'character_type_key', 'character_last_position','character_nb_quests']


class Discord(Resource):

    def get(self, name="", NPC_name=""):
        # print('{} / {}'.format(name, NPC_name))
        response = False
        if checkPseudo(name):
            search = db.hget('accounts_search', name)
            account = literal_eval(db.hget('accounts', search))
            for character in account["account_characters"]:
                if character["character_name"] == NPC_name:
                    response = literal_eval(db.hget(
                        'characters', character['character_key']))
                    for information in no_keep_information:
                        del response[information]
                    response['classe_name'] = json.loads(
                        db.hget('classes', response['class_key']))['class_name']
                    del response['class_key']
                    response['account_name'] = name
                    # print(response)
        if not response:
            abort(404, message="character {} doesn't exist".format(NPC_name))
        return response, 200


def checkPseudo(pseudo):
    # print(db.hget('accounts', UUID))
    if not db.hexists('accounts_search', pseudo):
        abort(404, message="Pseudo {} doesn't exist".format(pseudo))
    return True
