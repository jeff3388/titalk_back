from flask import abort, Response, request
from functools import wraps

# verify post data json key
def validate_json(*default_args):
    def decorator_validate_json(function_name):

        @wraps(function_name)
        def wrapper(*args):
            if not request.get_json():
                abort(Response('request must be json format'))

            json_object = request.get_json()
            for default_arg in default_args:
                if default_arg not in json_object:
                    abort(Response('You are missing this json key: {}'.format(str(default_arg))))

            return function_name(*args)

        return wrapper

    return decorator_validate_json