#!/usr/bin/env python3
import os
import pdb

import pytest
from collections import namedtuple
from mtm.components.mood.auth import Auth
from mtm.components.mood.channels import MMChannel

Account = namedtuple("Account", "username password code")
pwd = os.path.dirname(__file__) + "/"


@pytest.fixture(scope="function")
def test_account():
    return Account(
        **{"username": "18388232665", "password": "xy123456", "code": "123456"}
    )


@pytest.fixture(scope="function")
def login(request, test_account):
    auth = Auth(test_account.username, test_account.code)
    assert auth.login(), "login failed!"
    
    pdb.set_trace()
    request.addfinalizer(auth.logout)
    return auth


@pytest.fixture(scope="function")
def channel(login):
    return MMChannel(login.bearer)


@pytest.fixture(scope="function")
def audio_meta(channel):
    return channel.upload_audio(pwd + "test.mp3")


@pytest.fixture(scope="function")
def image_meta(channel):
    return channel.upload_audio(pwd + "test.jpg")
