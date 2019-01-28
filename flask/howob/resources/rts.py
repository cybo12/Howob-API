from flask_restful import reqparse, abort, Resource
from ast import literal_eval
from flask import jsonify, json, request
from uuid import uuid4
from db import db
import logging
from server_communication import communication_core


parser = reqparse.RequestParser()
parser.add_argument('quest_name', help='Error: {error_msg}')
parser.add_argument('quest_description', help='Error: {error_msg}')
parser.add_argument('quest_gold', help='Error: {error_msg}')
parser.add_argument('quest_experience', help='Error: {error_msg}')
parser.add_argument('nbr_spawns_to_kill', help='Error: {error_msg}')
parser.add_argument('nbr_remnants', help='Error: {error_msg}')
parser.add_argument('message', help='Error: {error_msg}')
parser.add_argument('game_key', help='Error: {error_msg}')
parser.add_argument('team_key', help='Error: {error_msg}')
parser.add_argument('quest_key', help='Error: {error_msg}')

NPC_UUID = "3d55d299-67bd-4162-a1e5-9c8dae37cdbc"
NPC_TRASH_UUID = "ecdf8e0b-2a85-4e33-aa3d-ded17a987a02"
"""
"UUID_NPC_QUEST_RTS":{
    "quest_name": {quest_name_RTS},
    "quest_description": {quest_description_RTS}, 
    "quest_gold": {quest_gold_RTS}, 
    "quest_experience": {quest_experience_RTS}, 
    "quest_type_key": 0, 
    "quest_advancement": {
        "id": {ID de classe des RTS Spawn (hardcordé)},
        "max_nbr": {nbr_spawns_to_kill},
        "current": 0,
        "class":
    },
}
"call_type": 1,
    "from": "RTS",
"payload": {
"""


class Rts(Resource):

    def get(self, UUID=""):
        responses = json.loads(db.hget('quests', NPC_UUID))
        # print(responses)
        return responses, 200

    def post(self):
        # print("no processed data receive : {}".format(request.data))
        # logging.info("post RTS")
        # logging.info(request.data)
        npc_quest = json.loads(db.hget('quests', NPC_UUID))
        args = parser.parse_args()
        if args.nbr_remnants:
            update = args.nbr_remnants
            data = json.loads(db.hget('characters', NPC_TRASH_UUID))
            data["character_last_position"] = data["character_last_position"]
            data["nbr_remnants"] = update
            key_to_delete = []
            players = db.hgetall('quests')
            for key in npc_quest:
                if(npc_quest[args.quest_key]["game_key"] == npc_quest[key]["game_key"]):
                    key_to_delete.append(key)
            for k, value in players.items():
                dict_value = literal_eval(value)
                for key in key_to_delete:
                    if key in dict_value:
                        del dict_value[key]
                db.hset('quests', k, json.dumps(dict_value))
            data["quest_key_1"] = key_to_delete[0]
            data["quest_key_2"] = key_to_delete[1]
            data_mq = {"call_type": 0, "from": "RTS", "payload": data}
            communication_core.rts_quest_add(data_mq)
            response = "monsters invocated"
        else:
            data = {}
            UUID = str(uuid4())
            data["quest_key"] = UUID
            data["team_key"] = args.team_key
            data["game_key"] = args.game_key
            data["quest_giver"] = NPC_UUID
            data["quest_name"] = args.quest_name
            data["quest_description"] = args.quest_description
            data["quest_gold"] = int(args.quest_gold)
            data["quest_type_key"] = 0
            data["quest_experience"] = int(args.quest_experience)
            data["quest_advancement"] = {
                "id": 12, "max_nbr": int(args.nbr_spawns_to_kill), "current": 0, "classe": 12}
            npc_quest[UUID] = data
            data["npc"] = json.loads(db.hget('characters', NPC_TRASH_UUID))
            data["npc"]["character_last_position"] = literal_eval(
                data["npc"]["character_last_position"])
            db.hset('quests', NPC_UUID, json.dumps(npc_quest))
            del data["team_key"]
            del data["game_key"]
            data_mq = {"call_type": 1, "from": "RTS", "payload": data}
            communication_core.rts_quest_add(data_mq)
            response = UUID
        # print(npc_quest)
        return response, 200

    def delete(self):
        db.hset('quests', NPC_UUID, "{}")
        return 'deleted', 204
 
    def put(self, UUID):
        #logging.info('put RTS')
        #logging.info(request.data)
        data = literal_eval(db.hget('quests', NPC_UUID))
        for key in data:
            if key == UUID:
                payload = {}
                payload["amount"] = data[key]["quest_gold"]
                payload["game_key"] = data[key]["game_key"]
                payload["team_key"] = data[key]["team_key"]
                payload["source"] = data[key]["quest_key"]
                if not communication_core.send_reward_rts(payload):
                    abort(404, message="RTS is down ?")
        return 'rewarded', 204
