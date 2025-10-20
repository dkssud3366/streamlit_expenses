
import redis


def connect_redis():
   rds = redis.from_url("redis://default:wudi0120@@T@redis-15226.c89.us-east-1-3.ec2.redns.redis-cloud.com:15226",\
                        decode_responses=True)
   return rds 

