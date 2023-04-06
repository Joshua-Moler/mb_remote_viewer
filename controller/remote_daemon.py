import socketio
import requests
import secrets
import time
import json
from urllib.parse import quote as urlEncodeBase
import hmac
from hashlib import sha1
from base64 import b64encode
sio = socketio.Client()


def urlEncode(str):
    return urlEncodeBase(str, '.')


def getOAuthConsumerKey():
    with open('remote_settings.json') as f:
        return json.load(f)["Consumer_Key"]


def getOAuthTokenKey():
    with open('remote_settings.json') as f:
        return json.load(f)["Token_Key"]


def getOAuthConsumerSecret():
    with open('remote_settings.json') as f:
        return json.load(f)["Consumer_Secret"]


def getOAuthTokenSecret():
    with open('remote_settings.json') as f:
        return json.load(f)["Token_Secret"]


def getOAuthString(method, url, parameters):
    print(parameters)
    andSymbol = urlEncode('&')
    encodedMethod = urlEncode(method)
    encodedurl = urlEncode(url)
    encodedParams = ''
    for key, value in dict(sorted(parameters.items())).items():
        print(key, value)
        encodedParams += f'{urlEncode(key)}{urlEncode("=")}{urlEncode(value)}{andSymbol}'
    encodedParams = encodedParams[:-len(andSymbol)]
    OAuthString = encodedMethod + '&' + encodedurl + '&' + encodedParams
    print(OAuthString)
    return OAuthString


def getSHA1Hash(key, str):
    return b64encode(hmac.new(bytes(key, 'utf-8'), bytes(str, 'utf-8'), sha1).digest()).decode()


def getAuth(method, url):
    params = {"oauth_nonce": secrets.token_urlsafe(),
              "oauth_timestamp": str(int(time.time())),
              "oauth_version": "1.0",
              "oauth_signature_method": "HMAC-SHA1",
              "oauth_consumer_key": getOAuthConsumerKey(),
              "oauth_token": getOAuthTokenKey()}
    OAuthString = getOAuthString(method, url, params)
    signature = urlEncode(getSHA1Hash(
        urlEncode(getOAuthConsumerSecret()) + '&' + urlEncode(getOAuthTokenSecret()), OAuthString))

    params["oauth_signature"] = signature
    toReturn = "OAuth "
    for key, value in params.items():
        toReturn += f'{key}="{value}", '
    return toReturn[:-2]


if __name__ == '__main__':
    @sio.event
    def connect():
        print('connected')

    @sio.event
    def connect_error(data):
        print(f"connection failed: {data}")

    @sio.event
    def disconnect():
        print('disconnected')

    @sio.on('set_state')
    def test(data):
        response = requests.post(
            'http://localhost:8080/remote/set/all', json=data)
        try:
            success, newState = response.json()
        except:
            success = False
            newState = {}

        # sio.emit('valve-put', newState['valves'])
        # sio.emit('pump-put', newState['pumps'])

        return success

    sio.connect('http://localhost:5000',
                auth=getAuth("POST", "http://localhost:5000"))
