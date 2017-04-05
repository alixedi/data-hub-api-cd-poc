from hashlib import sha256

import pytest

from datahub.core.utils import generate_signature, log_and_ignore_exceptions, string_to_bytes

# mark the whole module for db use
pytestmark = pytest.mark.django_db


def test_log_and_ignore_exceptions():
    """Ensure that exception does not bubble up."""
    try:
        with log_and_ignore_exceptions():
            raise Exception('test')
    except:  # noqa: B901;
        pytest.fail('Should not happen!')


data = (
    ('hello', bytes('hello', 'utf-8')),
    ({1, 2, 3}, {1, 2, 3}),
    ('&$%', bytes('&$%', 'utf-8')),
)
ids = (
    'string',
    'non string',
    'utf-8 string'
)


@pytest.mark.parametrize(('input', 'expected_output'), data, ids=ids)
def test_string_to_bytes(input, expected_output):
    """String to bytes."""
    assert string_to_bytes(input) == expected_output


def test_generate_signature():
    """Test auth signature generation."""
    path = 'http://www.foo.bar/hello'
    salt = 'foo'
    body = 'bar'
    expected_signature = sha256(bytes('/hellofoobar', 'utf-8')).hexdigest()
    assert generate_signature(path, salt, body) == expected_signature
