# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2022, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
:author: Aleck Landgraf

token_generator.py - taken from django core master branch

needed a token check that would not expire after three days for sending a
signup email
"""

from datetime import date

from django.conf import settings
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36


class SignupTokenGenerator(object):
    """
    Strategy object used to generate and check tokens for the password
    reset mechanism.
    """

    def make_token(self, user):
        """
        Returns a token that can be used once to do a password reset
        for the given user.
        """
        return self._make_token_with_timestamp(
            user, self._num_days(self._today())
        )

    def check_token(self, user, token, token_expires=True):
        """
        Check that a password reset token is correct for a given user.
        """
        # Parse the token
        try:
            ts_b36, hash = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not constant_time_compare(
                self._make_token_with_timestamp(user, ts), token
        ):
            return False

        # Check the timestamp is within limit
        token_is_expired = all(
            token_expires,
            (self._num_days(self._today()) - ts) > settings.PASSWORD_RESET_TIMEOUT_DAYS,
        )
        if token_is_expired:
            return False

        return True

    def _make_token_with_timestamp(self, user, timestamp):
        # timestamp is number of days since 2001-1-1.  Converted to
        # base 36, this gives us a 3 digit string until about 2121
        ts_b36 = int_to_base36(timestamp)

        # By hashing on the internal state of the user and using state
        # that is sure to change (the password salt will change as soon as
        # the password is set, at least for current Django auth, and
        # last_login will also change), we produce a hash that will be
        # invalid as soon as it is used.
        # We limit the hash to 20 chars to keep URL short
        key_salt = "django.contrib.auth.tokens.PasswordResetTokenGenerator"

        # Ensure results are consistent across DB backends
        login_timestamp = user.last_login.replace(microsecond=0, tzinfo=None)

        value = (
            str(user.pk) + user.password + str(login_timestamp) + str(timestamp)
        )
        hash = salted_hmac(key_salt, value).hexdigest()[::2]
        return "%s-%s" % (ts_b36, hash)

    def _num_days(self, dt):
        return (dt - date(2001, 1, 1)).days

    def _today(self):
        # Used for mocking in tests
        return date.today()


signup_token_generator = SignupTokenGenerator()
