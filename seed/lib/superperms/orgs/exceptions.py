# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2022, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
:author
"""


class TooManyNestedOrgs(Exception):
    """We only support one level of nesting."""


class UserNotInOrganization(Exception):
    """Raised when a user does not exist, or does not belong to an org."""


class InsufficientPermission(Exception):
    """Raised when a user attempts an action for which they're not allowed."""
