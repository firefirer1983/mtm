#!/usr/bin/env python3
import pytest
from collections import namedtuple
from mtm.components.mood.auth import Auth

Account = namedtuple("Account", "username password code")


@pytest.fixture(scope="function")
def test_account():
    return Account(
        **{"username": "18388232665", "password": "xy123456", "code": "123456"}
    )


@pytest.fixture(scope="function")
def login(request, test_account):
    auth = Auth(test_account.username, test_account.code)

    request.addfinalizer(auth.logout)
    return auth
