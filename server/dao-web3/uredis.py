import redis, json
from functools import wraps

redis_config = {
    'host': 'localhost',
    'port': 6379,
    'db': 9,
}

_redis = redis.from_url('redis://redis:6379')

def use_redis(expire_time = 30, specified_case = {}):
    def decorate(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            ex=30
            rk = func.__name__ + json.dumps(args) + json.dumps(kwargs)
            rv_s=_redis.get(rk)
            if rv_s is None:
                rv_s= json.dumps(func(*args, **kwargs))
                _redis.setex(rk, specified_case.get(rv_s, expire_time), rv_s)
            return json.loads(rv_s)
        return wrapped_function
    return decorate