import time
import requests
import json
from ast import literal_eval
from server_communication.mq import mq
from db import db
# import mailjet
from uuid import uuid4
import twitter
import urllib3
import logging
import sys

if sys.argv[1] == "prod":
    MQ_QUEUE = "rts"
else:
    MQ_QUEUE = "dev_rts"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

api = twitter.Api(consumer_key="consumer_key",
                  consumer_secret="consumer_secret",
                  access_token_key="access_token_key",
                  access_token_secret="access_token_secret")


def from_rts(payload):
    response = True
    try:
        mq.publish(json.dumps(payload))
        mq.publish(json.dumps((payload)), "discord")
    except Exception as e:
        logging.info(e)
        response = False
    return response


def from_mmo(payload, discord=False):
    response = True
    url = 'https://RTS/api/messages'
    headers = {'Content-Type': 'application/json'}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload),
                          auth=('user', 'PWD+'), verify=False)
        if r.status_code == 200:
            if not discord:
                from_rts(payload)
        else:
            logging.info(f"RTS SATUTS CODE: {r.status_code}")
            response = False
    except requests.exceptions.RequestException as e:
        response = False
        logging.info(e)
    return response


def from_discord(payload):
    response = True
    try:
        pd = dict(payload)
        if "message" in pd:
            if len(pd["message"]) > 1 and pd["message"] != " ":
                mq.publish(json.dumps(payload))
        if "from" in pd:
            pd["from"] = "MMO"
        from_mmo(pd, True)
    except Exception as e:
        logging.info(e)
        response = False
    return response


def post_twitter(payload):
    try:
        api.PostUpdate(payload)
    except Exception as e:
        e = literal_eval(str(e)[1:-1])
        logging.info(f"Twitter errors: {e['message']}")
    return True


def rts_quest_add(payload):
    mq.get_channel(MQ_QUEUE)
    mq.publish(json.dumps(payload), MQ_QUEUE)


def auth_RTS(pseudo, hashed_password):
    response = True
    payload = dict()
    payload["user_name"] = pseudo
    payload["hashed_password"] = hashed_password
    url = 'https://RTS/api/authentication_player'
    headers = {'Content-Type': 'application/json'}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload),
                          auth=('user', 'PWD+'), verify=False)
        if r.status_code == 200:
            if not db.hexists('accounts_search', pseudo):
                createRTSAccount(json.loads(r.text)["user_name"])
        else:
            logging.info(f"RTS SATUTS CODE: {r.status_code}")
            response = False
    except requests.exceptions.RequestException as e:
        response = False
        logging.info(e)
    return response


def createRTSAccount(user_name):
    print('Never connected on MMO, creation account for {}'.format(user_name))
    UUID = str(uuid4())
    # print(UUID)
    pre_data = dict()
    pre_data["account_characters"] = []
    pre_data["account_key"] = UUID
    pre_data["account_pseudo"] = user_name
    data = {UUID: json.dumps(pre_data)}
    # print(data)
    # print(type(data))
    db.hmset('accounts', data)
    db.hset('accounts_search', user_name, UUID)
    createMMOCharacter(UUID, user_name)


def createMMOCharacter(UUID, user_name):
    initial_data = {
        "account_key": UUID,
        "character_name": user_name,
        "character_level": 1,
        "character_experience": 0,
        "character_life": 20,
        "character_max_life": 20,
        "character_mana": 20,
        "character_max_mana": 20,
        "class_key": 0,
        "character_type_key": 1,
        "character_last_position": {
            "x": 0,
            "y": 5
        },
        "character_nb_quests": 0,
        "character_nb_gold": 2
    }
    headers = {'Content-Type': 'application/json'}
    url = "https://XX/api/character"
    r = requests.post(url, headers=headers, data=json.dumps(initial_data))
    # print(r.text)


def send_reward_rts(payload):
    response = True
    link = "https://RTS/api/interactions/money_gift/"
    url = f"{link}{payload['game_key']}/{payload['team_key']}"
    headers = {'Content-Type': 'application/json'}
    del payload["game_key"]
    del payload["team_key"]
    # logging.info(f"reward to RTS : {url}")
    # logging.info(f"payload : {payload}")
    try:
        r = requests.patch(url, headers=headers, data=json.dumps(payload),
                           auth=('user', 'PWD+'), verify=False)
        if r.status_code != 200:
            logging.info(f"RTS SATUTS CODE: {r.status_code}")
            response = False
    except requests.exceptions.RequestException as e:
        response = False
        logging.info(e)
    return response
