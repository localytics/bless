import os
import pytest

from bless.aws_lambda.bless_lambda import lambda_handler
from tests.ssh.vectors import EXAMPLE_RSA_PUBLIC_KEY, RSA_CA_PRIVATE_KEY_PASSWORD, \
    EXAMPLE_ED25519_PUBLIC_KEY


class Context(object):
    aws_request_id = 'bogus aws_request_id'
    invoked_function_arn = 'bogus invoked_function_arn'


VALID_TEST_REQUEST = {
    "remote_username": "user",
    "public_key_to_sign": EXAMPLE_RSA_PUBLIC_KEY,
    "command": "ssh user@server",
    "bastion_user": "user"
}

os.environ['AWS_REGION'] = 'us-west-2'


def test_basic_local_request():
    cert = lambda_handler(VALID_TEST_REQUEST, context=Context,
                          ca_private_key_password=RSA_CA_PRIVATE_KEY_PASSWORD,
                          entropy_check=False,
                          config_file=os.path.join(os.path.dirname(__file__), 'bless-test.cfg'))
    assert cert.startswith('ssh-rsa-cert-v01@openssh.com ')


def test_local_request_key_not_found():
    with pytest.raises(IOError):
        lambda_handler(VALID_TEST_REQUEST, context=Context,
                       ca_private_key_password=RSA_CA_PRIVATE_KEY_PASSWORD,
                       entropy_check=False,
                       config_file=os.path.join(os.path.dirname(__file__), 'bless-test-broken.cfg'))


def test_local_request_config_not_found():
    with pytest.raises(ValueError):
        lambda_handler(VALID_TEST_REQUEST, context=Context,
                       ca_private_key_password=RSA_CA_PRIVATE_KEY_PASSWORD,
                       entropy_check=False,
                       config_file=os.path.join(os.path.dirname(__file__), 'none'))


def test_local_request_invalid_pub_key():
    invalid_key_request = {
        "remote_username": "user",
        "public_key_to_sign": EXAMPLE_ED25519_PUBLIC_KEY,
        "command": "ssh user@server",
        "bastion_user": "user"
    }
    with pytest.raises(TypeError):
        lambda_handler(invalid_key_request, context=Context,
                       ca_private_key_password=RSA_CA_PRIVATE_KEY_PASSWORD,
                       entropy_check=False,
                       config_file=os.path.join(os.path.dirname(__file__), 'bless-test.cfg'))
