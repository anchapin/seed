# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2022, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
:author
"""
from rest_framework import serializers

from seed.models import AnalysisOutputFile


class AnalysisOutputFileSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(source='get_content_type_display')

    class Meta:
        model = AnalysisOutputFile
        fields = '__all__'
