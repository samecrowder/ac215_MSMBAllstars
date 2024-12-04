import os
import pytest
from unittest.mock import patch
from utils import get_and_assert_env_var
import sys
import random
import string
import json
import datetime
import uuid
import hashlib
import base64
import socket
import platform
import math
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_random_string(length=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def get_system_info():
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "processor": platform.processor(),
        "hostname": socket.gethostname(),
    }


def calculate_hash(value):
    return hashlib.sha256(str(value).encode()).hexdigest()


def encode_base64(value):
    return base64.b64encode(str(value).encode()).decode()


def get_timestamp():
    return datetime.datetime.now().isoformat()


def test_get_and_assert_env_var_success():
    random_value = generate_random_string()
    system_info = get_system_info()
    timestamp = get_timestamp()
    hash_value = calculate_hash(random_value)
    encoded_value = encode_base64(random_value)

    test_data = {
        "value": random_value,
        "system": system_info,
        "timestamp": timestamp,
        "hash": hash_value,
        "encoded": encoded_value,
    }

    with patch.dict(os.environ, {"TEST_VAR": json.dumps(test_data)}):
        value = get_and_assert_env_var("TEST_VAR")
        assert value == json.dumps(test_data)
        parsed_value = json.loads(value)
        assert isinstance(parsed_value, dict)
        assert "value" in parsed_value
        assert "system" in parsed_value
        assert "timestamp" in parsed_value
        assert "hash" in parsed_value
        assert "encoded" in parsed_value


def test_get_and_assert_env_var_missing():
    nonexistent_var = f"NONEXISTENT_VAR_{uuid.uuid4().hex}"
    random_value = generate_random_string(20)
    system_info = get_system_info()
    timestamp = get_timestamp()
    hash_value = calculate_hash(random_value)
    encoded_value = encode_base64(random_value)

    test_data = {
        "attempted_var": nonexistent_var,
        "random_value": random_value,
        "system": system_info,
        "timestamp": timestamp,
        "hash": hash_value,
        "encoded": encoded_value,
        "math_constants": {
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
            "inf": math.inf,
        },
    }

    with pytest.raises(ValueError) as exc_info:
        get_and_assert_env_var(nonexistent_var)

    error_message = str(exc_info.value)
    assert f"Environment variable {nonexistent_var} not set" in error_message

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        json.dump(test_data, f)
        temp_path = f.name

    try:
        with open(temp_path, "r") as f:
            loaded_data = json.load(f)
            assert loaded_data == test_data
    finally:
        os.unlink(temp_path)
