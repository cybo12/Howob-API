# -*- coding: UTF-8 -*-
from flask_restful import Api
import time
import datetime
import colors
from flask import Flask, g, request
from logging.config import dictConfig
import logging
import sys

from resources.account import Account
from resources.classe import Classe
from resources.character import Character
from resources.quest import Quest
from resources.rts import Rts
from resources.authentication import Authentication
from resources.messages import Message
from resources.discord import Discord
from resources.system import System
from resources.social import Social


##
# masi life: Dont be a Dict()
##
if sys.argv[1] == "prod":
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '%(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    # logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)
    api = Api(app)
    app.config['JSON_AS_ASCII'] = False

    DEBUG = False

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.error('Unhandled Exception: %s', (e))

    @app.before_request
    def start_timer():
        g.start = time.time()

    @app.after_request
    def log_request(response):
        now = time.time()
        duration = round(now - g.start, 2)
        dt = datetime.datetime.fromtimestamp(now).replace(microsecond=0)
        timestamp = dt + datetime.timedelta(hours=1)
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        host = request.host.split(':', 1)[0]
        args = dict(request.args)

        log_params = [
            ('time', timestamp, 'magenta'),
            ('status', response.status_code, 'yellow'),
            ('duration', duration, 'green'),
            ('method', request.method, 'blue'),
            ('path', request.path, 'blue'),
            ('ip', ip, 'red'),
            ('host', host, 'red'),
            ('params', args, 'blue')
        ]

        request_id = request.headers.get('X-Request-ID')
        if request_id:
            log_params.append(('request_id', request_id, 'yellow'))

        parts = []
        for name, value, color in log_params:
            part = colors.color("{}={}".format(name, value), fg=color)
            parts.append(part)
        line = " ".join(parts)

        app.logger.info(line)
        return response

    PORT = 5000
    app.logger.info(f"{str(sys.argv[1]).upper()} MODE")

else:
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    app = Flask(__name__)
    api = Api(app)
    app.config['JSON_AS_ASCII'] = False
    PORT = 5001
    app.logger.info("DEV MODE")
    DEBUG = True


@app.errorhandler(404)
def page_not_found(e):
    return "Forbidden", 403


@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', (error))
    return error, 500


#
# Actually setup the Api resource routing here
##


api.add_resource(Account, '/account', '/account/<string:UUID>')
api.add_resource(Classe, '/classes', '/classe/<string:UUID>')
api.add_resource(Character, '/character', '/characters',
                 '/character/<string:UUID>')
api.add_resource(Quest, '/quests', '/quest/<string:UUID>')
api.add_resource(Rts, '/rts', '/rts/<string:UUID>')
api.add_resource(Authentication, '/auth')
api.add_resource(Message, '/messages')
api.add_resource(Discord, '/discord/<string:name>/<string:NPC_name>')
api.add_resource(System, '/system/<string:payload>', '/system')
api.add_resource(Social, '/social/<string:payload>', '/social')


# main parameter of Flask Application
if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)
