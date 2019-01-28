from flask_restful import reqparse, Resource
import datetime
import pyspeedtest
from multiprocessing import Process, Array
from db import db
import logging

parser = reqparse.RequestParser()
parser.add_argument('utc_time', help='Error: {error_msg}')
parser.add_argument('nbr_players', help='Error: {error_msg}')
parser.add_argument('nbr_quests', help='Error: {error_msg}')


class System(Resource):

    def post(self):
        args = parser.parse_args()
        db.hmset('status', args)
        return "coucou", 200

    def get(self):
        data = db.hgetall('status')
        date = datetime.datetime.strptime(
            data["utc_time"], '%d-%m-%y %H:%M:%S')
        data['utc_time'] = str(datetime.datetime.utcnow() - date)[:-7]
        l_mmo = Array('c', b'unreachable')
        p = Process(target=get_latency, args=(
            "XX:9091", l_mmo,))
        p.start()
        p.join(4)
        if p.is_alive():
            p.terminate()
            p.join()
        mmo = {"Howob": l_mmo.value.decode()}
        l_rts = Array('c', b'unreachable')
        p2 = Process(target=get_latency, args=(
            "RTS", l_rts,))
        p2.start()
        p2.join(4)
        if p2.is_alive():
            p2.terminate()
            p2.join()
        rts = {"Boomcraft": l_rts.value.decode()}

        data["latency"] = {}
        data["latency"].update(mmo)
        data["latency"].update(rts)
        return data, 200


def get_latency(url, var):
    try:
        st = pyspeedtest.SpeedTest(url)
        val = "{:.2f} ms".format(st.ping()).encode()
        var.value = val
    except Exception as e:
        print(e)
