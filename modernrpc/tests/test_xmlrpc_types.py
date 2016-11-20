# coding: utf-8
import datetime
import re

from django.utils.six.moves import xmlrpc_client


def test_xrpc_bool(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_true()

    assert type(result) == bool
    assert result is True

    result = client.get_false()

    assert type(result) == bool
    assert result is False


def test_xrpc_null(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    assert client.get_null() is None


def test_xrpc_numeric(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')

    result = client.get_int()
    assert type(result) == int
    assert result == 42

    result = client.get_negative_int()
    assert type(result) == int
    assert result == -42

    result = client.get_float()
    assert type(result) == float
    assert result == 3.14


def test_xrpc_string(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_string()

    # Unlike JSON-RPC, XML-RPC always return a str. That means the result is unicode
    # in Python 3 and ASCII in Python 2. This may be addressed in the future
    assert type(result) == str
    assert result == 'abcde'


def test_xrpc_input_string(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_data_type('abcd')

    # Python 2 : "<type 'str'>"
    # Python 3 : "<class 'str'>"
    assert re.match(r"<(class|type) 'str'>", result)


def test_xrpc_bytes(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_bytes()

    assert result == b'abcde'


def test_xrpc_date(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_date()

    assert isinstance(result, xmlrpc_client.DateTime)
    assert '19870602' in str(result)
    assert '08:45:00' in str(result)

    try:
        # Python 3
        client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/', use_builtin_types=True)
    except TypeError:
        # Python 3
        client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/', use_datetime=True)

    result = client.get_date()

    assert isinstance(result, datetime.datetime)

    assert result.year == 1987
    assert result.month == 6
    assert result.day == 2
    assert result.hour == 8
    assert result.minute == 45
    assert result.second == 0


def test_xrpc_date_2(live_server):

    date = datetime.datetime(1990, 1, 1, 0, 0, 0)

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_data_type(date)

    # Python 2 : "<type 'datetime.datetime'>"
    # Python 3 : "<class 'datetime.datetime'>"
    assert re.match(r"<(class|type) 'datetime.datetime'>", result)


def test_xrpc_date_3(live_server):

    try:
        # Python 3
        client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/', use_builtin_types=True)
    except TypeError:
        # Python 3
        client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/', use_datetime=True)
    date = datetime.datetime(2000, 6, 3, 0, 0, 0)
    result = client.add_one_month(date)

    # JSON-RPC will transmit the input argument and the result as standard string
    assert result.year == 2000
    assert result.month == 7
    assert result.day == 4
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0


def test_xrpc_list(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_list()

    assert type(result) == list
    assert result == [1, 2, 3, ]


def test_xrpc_struct(live_server):

    client = xmlrpc_client.ServerProxy(live_server.url + '/all-rpc/')
    result = client.get_struct()

    assert type(result) == dict
    assert result == {'x': 1, 'y': 2, 'z': 3, }
