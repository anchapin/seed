"""
:copyright (c) 2014 - 2022, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
:author
"""
from django.conf import settings
from django.http import HttpResponse


def robots_txt(request, allow=False):
    try:
        if settings.ENV.lower() != "production":
            return HttpResponse(
                "User-agent: *\nDisallow: /", content_type="text/plain"
            )
        else:
            return HttpResponse(
                "User-agent: *\nAllow: /", content_type="text/plain"
            )
    except BaseException:
        pass
    if allow:
        return HttpResponse("User-agent: *\nAllow: /", content_type="text/plain")
    else:
        return HttpResponse(
            "User-agent: *\nDisallow: /", content_type="text/plain"
        )
