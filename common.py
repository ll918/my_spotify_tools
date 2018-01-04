import json

import requests


def get_request(url, headers={}, payload={}):
    r = requests.get(url, headers=headers, data=payload)
    try:
        r.raise_for_status()
    except Exception as e:
        print('There was a problem: %s' % e)
    return r


def post_request(url, headers={}, payload={}):
    r = requests.post(url, headers=headers, data=payload)
    try:
        r.raise_for_status()
    except Exception as e:
        print('There was a problem: %s' % e)
    return r


def save_to_json(data, file):
    try:
        with open(file, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print('There was a problem: %s' % e)
