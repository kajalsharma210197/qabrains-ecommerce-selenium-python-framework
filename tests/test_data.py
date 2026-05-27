"""Centralized test data for TDD test cases."""

import pytest

HOMEPAGE_URL = "https://practice.qabrains.com/ecommerce"

DEFAULT_LOGIN_USER = ("test@qabrains.com", "Password123")

LOGIN_USERS = [
    pytest.param("test@qabrains.com", "Password123", id="test-user"),
]
