from flask import Flask, request, jsonify, session, abort
from urllib.parse import quote as urlEncodeBase
from hashlib import sha1
import hmac
from base64 import b64encode
import time
import sqlite3
from collections import OrderedDict


valveNum = 27
pumpNum = 2

nonceList = {}
maxTimestampGap = 10


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# def ReformatURL(url):
#     return url.replace('://', '%3A').replace('/', '%2F')


# def getOAuthString(method, url, authHeader):
#     return method + '&' + ReformatURL(url) + '&' + \
#         'oauth_consumer_key' + '%3D' + authHeader['oauth_consumer_key'] + '%26' + \
#         'oauth_nonce' + '%3D' + authHeader['oauth_nonce'] + '%26' + \
#         'oauth_signature_method' + '%3D' + authHeader['oauth_signature_method'] + '%26' + \
#         'oauth_timestamp' + '%3D' + authHeader['oauth_timestamp'] + '%26' + \
#         'oauth_token' + '%3D' + authHeader['oauth_token']

def getSafeSQL(code):
    return code.replace(' ', '')


def getClientSecret(clientKey):
    clientKey = getSafeSQL(clientKey)
    db_connection = sqlite3.connect('clients.db')
    sqlCursor = db_connection.cursor()
    sqlCursor.execute(
        f"SELECT client_secret from clients WHERE client_key='{clientKey}'")
    clientSecret = sqlCursor.fetchone()

    if clientSecret:
        return clientSecret[0].encode('utf-8')
    return b''


def getTokenSecret(tokenKey):
    tokenKey = getSafeSQL(tokenKey)
    db_connection = sqlite3.connect('clients.db')
    sqlCursor = db_connection.cursor()
    sqlCursor.execute(
        f"SELECT token_secret FROM tokens WHERE token_key='{tokenKey}'"
    )
    tokenSecret = sqlCursor.fetchone()

    if tokenSecret:
        return tokenSecret[0].encode('utf-8')
    return b''


def urlEncode(str):
    return urlEncodeBase(str, '.')


def cleanNonce():
    canFree = []
    for nonce, timestamp in nonceList.items():
        if time.time() - timestamp > maxTimestampGap:
            canFree.append(nonce)
    for nonce in canFree:
        del nonceList[nonce]


def verifyNonce(nonce):
    valid = False
    if nonce not in nonceList:
        valid = True
    nonceList[nonce] = time.time()

    cleanNonce()

    return valid


def verifyTimestamp(timestamp):
    if time.time() - int(timestamp) >= maxTimestampGap:
        return False
    return True


def getOAuthString(method, url, parameters):
    andSymbol = urlEncode('&')
    encodedMethod = urlEncode(method)
    encodedurl = urlEncode(url)
    encodedParams = ''
    for key, value in dict(sorted(parameters.items())).items():
        if key != 'oauth_signature':
            encodedParams += f'{urlEncode(key)}{urlEncode("=")}{urlEncode(value)}{andSymbol}'
    encodedParams = encodedParams[:-len(andSymbol)]
    return encodedMethod + '&' + encodedurl + '&' + encodedParams


def getSHA1Hash(key, str):
    return b64encode(hmac.new(bytes(key, 'utf-8'), bytes(str, 'utf-8'), sha1).digest()).decode()


def validateHeader(httpMethod, path, header, tls_ssl=False):
    if "Authorization" not in header:
        return False
    authHeader = header["Authorization"].replace("\"", "").\
        split(None, 1)[-1].split(", ")
    authDict = dict(item.split("=") for item in authHeader)

    nonce = verifyNonce(authDict['oauth_nonce'])
    timestamp = verifyTimestamp(authDict['oauth_timestamp'])
    if not (nonce and timestamp):
        return False

    prefix = 'https://' if tls_ssl else 'http://'

    oauthHost = prefix + header["Host"] + path
    oauthString = getOAuthString(httpMethod, oauthHost, authDict)
    clientSecret = getClientSecret(authDict['oauth_consumer_key'])
    tokenSecret = getTokenSecret(authDict['oauth_token'])
    validSignature = urlEncode(getSHA1Hash(
        urlEncode(clientSecret)+'&'+urlEncode(tokenSecret), oauthString))
    # print(header)
    #print(authDict['oauth_signature'], validSignature)

    return authDict['oauth_signature'] == validSignature


data = OrderedDict({"Temperatures": {"PRP": 1000, "RGP": 500, "CFP": 300, "STP": 500},
        "Pressures": {"P1": 53, "P2": 6, "P3": 91, "P4": 90},
        "Flow": {},
        "Valves": {},
        "Pumps": {},
        "Status": {"": "Manual"}
        })


@app.route('/Temperatures', methods=["GET", "PUT"])
def Temperatures():
    if request.method == 'GET':
        print(request.headers)
        if validateHeader('GET', '/Temperatures', request.headers):
            return jsonify(data["Temperatures"])
        abort(401)
        # header = request.headers["Authorization"].replace("\"", "")
        # hsplit = header.split(None, 1)[-1].split(", ")
        # res = dict(item.split("=") for item in hsplit)
        # oauthString = getOAuthString(
        #     'GET', 'http://localhost:5000/Temperatures', res)
        # print(oauthString)
        # validSignature = urlEncode(getSHA1Hash(urlEncode('client_secret') +
        #                                        '&'+urlEncode('resource_owner_secret'), oauthString))
        # print(validSignature)
        # return {}

    #     if res['oauth_signature'] != validSignature or not (verifyNonce(res['oauth_nonce']) and verifyTimestamp(res['oauth_timestamp'])):
    #         abort(401)
    #     return jsonify(data["Temperatures"])

    elif request.method == 'PUT':
        if validateHeader('PUT', '/Temperatures', request.headers):
            values = request.get_json()
            for key, value in values.items():
                data["Temperatures"][key] = value
            print('\n\n', data['Temperatures'])
            return jsonify(data["Temperatures"])
        abort(401)


@app.route('/Pressures', methods=["GET", "PUT"])
def Pressures():
    if request.method == 'GET':
        if validateHeader('GET', '/Pressures', request.headers):
            return jsonify(data["Pressures"])
        abort(401)

    elif request.method == 'PUT':
        if validateHeader('PUT', '/Pressures', request.headers):
            values = request.get_json()
            for key, value in values.items():
                data["Pressures"][key] = value
            print('\n\n', data['Pressures'])
            return jsonify(data["Pressures"])
        abort(401)


@app.route('/Flow', methods=["GET", "PUT"])
def Flow():
    if request.method == 'GET':
        if validateHeader('GET', '/Flow', request.headers):
            return jsonify(data["Flow"])
        abort(401)

    elif request.method == 'PUT':
        if validateHeader('PUT', '/Flow', request.headers):
            values = request.get_json()
            for key, value in values.items():
                data["Flow"][key] = value
            print('\n\n', data['Flow'])
            return jsonify(data["Flow"])
        abort(401)


@app.route('/Valves', methods=["GET", "PUT"])
def Valves():
    if request.method == 'GET':
        if validateHeader('GET', '/Valves', request.headers):
            return jsonify(data["Valves"])
        abort(401)

    elif request.method == 'PUT':
        if validateHeader('PUT', '/Valves', request.headers):
            values = request.get_json()
            for key, value in values.items():
                data["Valves"][key] = value
            print('\n\n', data['Valves'])
            return jsonify(data["Valves"])
        abort(401)


@app.route('/Pumps', methods=["GET", "PUT"])
def Pumps():
    if request.method == 'GET':
        if validateHeader('GET', '/Pumps', request.headers):
            return jsonify(data["Pumps"])
        abort(401)

    elif request.method == 'PUT':
        if validateHeader('PUT', '/Pumps', request.headers):
            values = request.get_json()
            for key, value in values.items():
                data["Pumps"][key] = value
            print('\n\n', data['Pumps'])
            return jsonify(data["Pumps"])
        abort(401)


@app.route('/All', methods=["GET"])
def All():
    if request.method == 'GET':
        if validateHeader('GET', '/All', request.headers):
            return jsonify(data)
    abort(401)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
