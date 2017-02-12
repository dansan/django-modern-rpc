# coding: utf-8
"""
This module define a very simple JSON-RPC ServerProxy, very similar to the one defined in Python internal for XML-RPC.
This class is used to simplify tests definition
"""
import json
import random

import django
import pytest
import requests
from django.utils.six.moves import urllib_parse
from requests.auth import HTTPBasicAuth

from modernrpc.exceptions import RPC_CUSTOM_ERROR_BASE, RPC_METHOD_NOT_FOUND


class JsonRpcFault(Exception):

    def __init__(self, faultCode, faultString, **extra):
        self.faultCode = faultCode
        self.faultString = faultString
        self.extra = extra

    def __str__(self):
        return "Error {}: {}".format(self.faultCode, self.faultString)


class ProtocolError(Exception):
    pass


class _RpcCall:

    def __init__(self, send, name):
        self.__send = send
        self.__name = name

    def __getattr__(self, name):
        return _RpcCall(self.__send, "%s.%s" % (self.__name, name))

    def __call__(self, *args):
        return self.__send(self.__name, args)


class ServerProxy:

    def __init__(self, url, auth_uname=None, auth_pwd=None):
        self.url = url

        parsed_url = urllib_parse.urlparse(url)
        username = parsed_url.username or auth_uname
        password = parsed_url.password or auth_pwd
        self.auth = False
        if username and password:
            self.auth = True
            self.username = username
            self.password = password

    def send_payload(self, methodName, params=None):
        headers = {'content-type': 'application/json'}
        payload = {
            "method": methodName,
            "params": params or [],
            "jsonrpc": "2.0",
            "id": random.randint(1, 1000),
        }
        auth = HTTPBasicAuth(username=self.username, password=self.password) if self.auth else None
        req_data = json.dumps(payload, cls=django.core.serializers.json.DjangoJSONEncoder)

        result = requests.post(self.url, data=req_data, headers=headers, auth=auth)

        if result.status_code != 200:
            raise ProtocolError

        response = result.json()
        if 'error' in response:
            raise JsonRpcFault(response['error']['code'], response['error']['message'])
        elif 'result' in response:
            return response['result']
        else:
            raise JsonRpcFault(RPC_CUSTOM_ERROR_BASE, 'Invalid JSON reponse')

    def __getattr__(self, name):
        return _RpcCall(self.send_payload, name)


# Tests
# These tests are performed against the free Guru JSON-RPC Tester
# If at some point the website is down, we will think about making request on another remote.
def test_simple_call():
    client = ServerProxy("https://gurujsonrpc.appspot.com/guru")
    result = client.guru.test("JSON")
    assert result == "Hello JSON!"


def test_simple_call_2():
    client = ServerProxy("https://gurujsonrpc.appspot.com/guru")
    result = client.system.listMethods()
    assert type(result) == list
    assert 'system.listMethods' in result
    assert 'guru.test' in result


def test_undefined_method():
    client = ServerProxy("https://gurujsonrpc.appspot.com/guru")

    with pytest.raises(JsonRpcFault) as excinfo:
        client.non.existing.method()

    assert excinfo.value.faultCode == RPC_METHOD_NOT_FOUND
    assert "no such method" in excinfo.value.faultString
    assert "no such method" in str(excinfo)


def test_invalid_response():

    client = ServerProxy("http://echo.jsontest.com/xxx/vvv")

    with pytest.raises(JsonRpcFault) as excinfo:
        client.invalide.method()

    assert excinfo.value.faultCode == RPC_CUSTOM_ERROR_BASE
    assert "Invalid JSON reponse" in excinfo.value.faultString
    assert "Invalid JSON reponse" in str(excinfo)
