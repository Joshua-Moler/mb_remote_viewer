from flask import Flask, request, jsonify, session, abort
from urllib.parse import quote as urlEncodeBase
from hashlib import sha1
import hmac
from base64 import b64encode
import time
import sqlite3
from collections import OrderedDict
import requests
from flask_socketio import SocketIO
from flask_socketio import ConnectionRefusedError
import secrets

import bcrypt

from enum import Enum

CLIENT_ACCESS_LEVEL = Enum(
    "CLIENT_ACCESS_LEVEL", "REMOTE_VIEWER_CLIENT PROVIDER_CLIENT ADMIN NO_ACCESS")

clientAccess = {
    '___IB_PROTOTYPE_SOFTWARE___': CLIENT_ACCESS_LEVEL.PROVIDER_CLIENT,
    '___MB_PROTOTYPE_SOFTWARE___': CLIENT_ACCESS_LEVEL.REMOTE_VIEWER_CLIENT}

valveNum = 27
pumpNum = 2

nonceList = {}
maxTimestampGap = 10

userResources = {}


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

def getSafeSQL(*code):
    if len(code) == 1:
        return code[0].replace(' ', '')
    r = []
    for c in code:
        r.append(c.replace(' ', ''))
    return r


def getClientSecret(clientKey):
    clientKey = getSafeSQL(clientKey)
    db_connection = sqlite3.connect('clients.db')
    sqlCursor = db_connection.cursor()
    sqlCursor.execute(
        f"SELECT client_secret from clients WHERE client_key='{clientKey}'")
    clientSecret = sqlCursor.fetchone()
    db_connection.close()
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
    db_connection.close()
    if tokenSecret:
        return tokenSecret[0].encode('utf-8')
    return b''


def authenticateUser(username, password):
    db_connection = sqlite3.connect('clients.db')
    sqlCursor = db_connection.cursor()

    hashedPassword = sqlCursor.execute(
        f"SELECT password FROM user_credentials WHERE username=?", (username, ))
    passwordRetrieved = hashedPassword.fetchone()
    if not passwordRetrieved:
        return {"authenticated": False}
    valid = bcrypt.checkpw(password.encode(
        'utf-8'), passwordRetrieved[0].encode('utf-8'))

    tokenKey = secrets.token_hex(16)
    tokenSecret = secrets.token_hex(64)

    sqlCursor.execute(
        "SELECT resource FROM user_access WHERE username=?", (username, ))

    userResource = sqlCursor.fetchone()[0]

    userResources[tokenKey] = userResource

    sqlCursor.execute(
        "INSERT INTO tokens (token_key, token_secret) VALUES(?, ?)", (tokenKey, tokenSecret))

    db_connection.commit()
    db_connection.close()

    return {"authenticated": valid, "tokenKey": tokenKey, 'tokenSecret': tokenSecret}


def registerProviderClient(serialNumber):
    serialNumber = getSafeSQL(serialNumber)
    db_connection = sqlite3.connect('clients.db')
    sqlCursor = db_connection.cursor()

    sqlCursor.execute(
        f"SELECT EXISTS(SELECT 1 FROM recognized_serial_numbers WHERE serial_number='{serialNumber}' AND registered='{False}')"
    )

    if not sqlCursor.fetchone()[0]:
        return False

    while True:
        clientKey = secrets.token_hex(16)
        sqlCursor.execute(
            f"SELECT EXISTS(SELECT 1 FROM clients WHERE client_key='{clientKey}')"
        )
        if sqlCursor.fetchone()[0]:
            break
    clientKey = clientKey + serialNumber + str(time.time())
    clientSecret = secrets.token_hex(256)
    sqlCursor.execute("INSERT INTO clients VALUES (?, ?)",
                      (clientKey, clientSecret))
    sqlCursor.execute(
        f"UPDATE recognized_serial_numbers SET registered={True} WHERE serial_number='{serialNumber}'")
    db_connection.commit()
    db_connection.close()

    return True


def removeTokenAccess(token):
    db_connection = sqlite3.connect('clients.db')
    sqlCursor = db_connection.cursor()
    sqlCursor.execute("DELETE FROM tokens WHERE token_key=?", (token, ))
    db_connection.commit()
    db_connection.close()


def addRemoteUser(header, user):
    client = header["Authorization"]["oauth_consumer_key"]
    if 'id' and 'token' in user:
        client, user['id'], user['token'] = getSafeSQL(
            client, user['id'], user['token'])
        db_connection = sqlite3.connect('clients.db')
        sqlCursor = db_connection.cursor()
        sqlCursor.execute(
            f"CREATE TABLE ${client}_remote_users (user_id, user_token)"
        )
        sqlCursor.execute(
            f"INSERT INTO ${client}_remote_users VALUES(?, ?)",
            [user['id'], user['token']]
        )
        db_connection.commit()
        db_connection.close()


def getClientType(header):
    key = header["Authorization"]["oauth_consumer_key"]
    if key in clientAccess:
        return clientAccess[key]
    return CLIENT_ACCESS_LEVEL.NO_ACCESS


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
    OAuthString = encodedMethod + '&' + encodedurl + '&' + encodedParams
    return OAuthString


def getSHA1Hash(key, str):
    return b64encode(hmac.new(bytes(key, 'utf-8'), bytes(str, 'utf-8'), sha1).digest()).decode()


def getAuthTokenKey(header):
    if 'Authorization' not in header:
        return ""
    authHeader = header["Authorization"].replace("\"", "").\
        split(None, 1)[-1].split(", ")
    authDict = dict(item.split("=") for item in authHeader)
    return authDict["oauth_token"]


def getAuthConsumerKey(header):
    if 'Authorization' not in header:
        return None
    try:
        authHeader = header["Authorization"].replace("\"", "").\
            split(None, 1)[-1].split(", ")
        authDict = dict(item.split("=") for item in authHeader)
        return authDict["oauth_consumer_key"]
    except Exception as e:
        print(e)
        return None


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
    if "Host" in header:
        oauthHost = prefix + header["Host"] + path
    else:
        oauthHost = path
    oauthString = getOAuthString(httpMethod, oauthHost, authDict)
    clientSecret = getClientSecret(authDict['oauth_consumer_key'])
    tokenSecret = getTokenSecret(authDict['oauth_token'])
    validSignature = urlEncode(getSHA1Hash(
        urlEncode(clientSecret)+'&'+urlEncode(tokenSecret), oauthString))

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
            return jsonify(data["Pumps"])
        abort(401)


@app.route('/All', methods=["GET"])
def All():
    if request.method == 'GET':
        if validateHeader('GET', '/All', request.headers):
            return jsonify(data)
        abort(401)


@app.route('/State', methods=['GET'])
def GetState():
    if request.method == 'GET':
        if validateHeader('GET', '/State', request.headers):
            return jsonify({"valves": data["Valves"], "pumps": data["Pumps"]})
        abort(401)


@app.route('/State/Set', methods=["POST"])
def StateSet():
    if request.method == 'POST':
        if validateHeader('POST', '/State/Set', request.headers):
            resource = userResources[getAuthTokenKey(request.headers)]
            success, newState = sendControlState(request.get_json(), resource)
            return jsonify([success, newState])
        abort(401)


@app.route("/Remote/Logout", methods=["POST"])
def LogoutRemote():
    if request.method == 'POST':
        if validateHeader('POST', '/Remote/Logout', request.headers):
            tokenKey = getAuthTokenKey(request.headers)
            removeTokenAccess(tokenKey)
            return jsonify([True])
        abort(401)


@app.route('/Remote/Auth', methods=["POST"])
def AuthRemote():
    if request.method == 'POST':
        if validateHeader('POST', '/Remote/Auth', request.headers):
            creds = request.json
            if 'username' and 'password' not in creds:
                abort(422)

            return jsonify(authenticateUser(creds['username'], creds['password']))
        abort(401)


@app.route('/Remote/Grant-User-Remote-Access', methods=["POST"])
def GrantUserRemoteAccess():
    data = request.get_json()
    if request.method == 'POST' and 'user' in data:
        if validateHeader('POST', '/Remote/Grant-User-Remote-Access', request.headers) and \
                getClientType(request.headers) == CLIENT_ACCESS_LEVEL.PROVIDER_CLIENT:
            addRemoteUser(request.headers, data['user'])
            return jsonify([True])
        abort(401)


def getNewConsumerKey(seed):
    return secrets.token_hex()


@app.route('/Remote/Register-Provider-Client', methods=["POST"])
def RegisterProviderClient():
    data = request.get_json()
    if request.method == 'POST' and 'serial_number' in data:
        if validateHeader('POST', '/Remote/Register-Provider-Client', request.headers):
            serialNumber = data['serial_number']
            registerProviderClient(serialNumber=serialNumber)


socketio = SocketIO(app)
sids = {}


def sendControlState(state, to):
    addr = sids[to]
    valves = {ii.lower(): not state[ii]
              for ii in state if ii.lower()[0] == 'v'}
    pumps = {ii.upper(): state[ii] for ii in state if ii.upper()[0:2] == 'PM'}
    success, newState = socketio.call(
        'set_state', {'valves': valves, 'pumps': pumps}, to=addr)
    # print(success, returnState)
    return success, newState


@socketio.on('connect')
def test_connect(auth):
    token = getAuthConsumerKey({"Authorization": auth})
    if token:
        sids[token] = request.sid
    print("New Websocket Connection.\n", sids)
    authenticated = validateHeader(
        "POST", "http://localhost:5000", {"Authorization": auth})

    if not authenticated:
        return False


@socketio.on('disconnect')
def disconnect():
    sid = request.sid
    toDelete = None
    for token in sids:
        if sids[token] == sid:
            toDelete = token
    if toDelete in sids:
        del sids[toDelete]


@app.route("/test")
def oauthtesting():
    print('OAuthTesting')
    if request.method == 'GET':
        print(request.headers)
        if validateHeader('GET', '/test', request.headers):
            return [True]
        abort(401)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
