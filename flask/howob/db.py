import redis
import sys

if sys.argv[1] == "prod":
    HOST = 'redis_master_1'
else:
    HOST = 'XX'

db = redis.Redis(host=HOST, port=6379, db=0,
                 password='PWD', decode_responses=True)
