from flask_restful import reqparse, abort, Resource
from flask import make_response, request
from db import db
from server_communication import communication_core

parser = reqparse.RequestParser()
parser.add_argument('user_name', help='Error: {error_msg}')
parser.add_argument('message', help='Error: {error_msg}')
parser.add_argument('date_time', help='Error: {error_msg}')
parser.add_argument('important', help='Error: {error_msg}')
parser.add_argument('from', help='Error: {error_msg}')
parser.add_argument('image_url', help='Error: {error_msg}')


"""
{
  user_name:string
  date_time: datetime int
  important:boolean
  from:"RTS"
}
"""
"""
        payload = {
            'user_name': 'satellite One',
            'message': 'cest quoi des nodes',
            'date_time': 1548376491,
            'important': 'false',
            'from': 'MMO'
        }
"""


class Message(Resource):

    def post(self):
        # print("no processed data receive : {}".format(request.data))
        args = parser.parse_args()
        if not args.message:
            args.message = " "
        if args['from'] == 'MMO':
            if not communication_core.from_mmo(args):
                abort(404, message="RTS IS DOWN")
        elif args['from'] == 'RTS':
            if not communication_core.from_rts(args):
                abort(404, message="we are not enable sorry(not sorry)")
        else:
            if not communication_core.from_discord(args):
                abort(404, message="Discord bot is down.")
        return make_response("message sent", 204)


def checkPseudo(pseudo):
    # print(db.hget('accounts', UUID))
    if not db.hexists('accounts_search', pseudo):
        abort(404, message="Pseudo {} doesn't exist".format(pseudo))
    return True
