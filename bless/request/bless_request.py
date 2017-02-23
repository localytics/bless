"""
.. module: bless.request.bless_request
    :copyright: (c) 2016 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import ipaddress
import re
from marshmallow import Schema, fields, post_load, ValidationError

# man 8 useradd
USERNAME_PATTERN = re.compile('[a-z_][a-z0-9_-]*[$]?\Z')


def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        raise ValidationError('Invalid IP address.')


def validate_user(user):
    if len(user) > 32:
        raise ValidationError('Username is too long')
    if USERNAME_PATTERN.match(user) is None:
        raise ValidationError('Username contains invalid characters')


class BlessSchema(Schema):
    bastion_user = fields.Str(validate=validate_user)
    public_key_to_sign = fields.Str()
    remote_username = fields.Str(validate=validate_user)

    @post_load
    def make_bless_request(self, data):
        return BlessRequest(**data)


class BlessRequest:
    def __init__(self, bastion_user, public_key_to_sign,
                 remote_username):
        """
        A BlessRequest must have the following key value pairs to be valid.
        :param bastion_user: The user on the bastion, who is initiating the SSH request.
        :param public_key_to_sign: The id_rsa.pub that will be used in the SSH request.  This is
        enforced in the issued certificate.
        :param remote_username: The username on the remote server that will be used in the SSH
        request.  This is enforced in the issued certificate.
        """
        self.bastion_user = bastion_user
        self.public_key_to_sign = public_key_to_sign
        self.remote_username = remote_username

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
