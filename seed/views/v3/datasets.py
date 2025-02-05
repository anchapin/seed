# encoding: utf-8
"""
:copyright (c) 2014 - 2022, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
:author
"""

import logging

from django.http import JsonResponse
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action

from seed.data_importer.models import ImportRecord
from seed.decorators import ajax_request_class, require_organization_id_class
from seed.lib.superperms.orgs.decorators import has_perm_class
from seed.lib.superperms.orgs.models import Organization, OrganizationUser
from seed.models import obj_to_dict
from seed.utils.api import OrgMixin, api_endpoint_class
from seed.utils.api_schema import (
    AutoSchemaHelper,
    swagger_auto_schema_org_query_param
)
from seed.utils.time import convert_to_js_timestamp

_log = logging.getLogger(__name__)


class DatasetViewSet(viewsets.ViewSet, OrgMixin):
    raise_exception = True

    @swagger_auto_schema_org_query_param
    @require_organization_id_class
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('can_view_data')
    def list(self, request):
        """
        Retrieves all datasets for the user's organization.
        """

        org_id = self.get_organization(request)
        org = Organization.objects.get(pk=org_id)
        datasets = []
        for d in ImportRecord.objects.filter(super_organization=org):
            importfiles = [obj_to_dict(f) for f in d.files]
            dataset = obj_to_dict(d)
            dataset['importfiles'] = importfiles
            if d.last_modified_by:
                dataset['last_modified_by'] = d.last_modified_by.email
            dataset['updated_at'] = convert_to_js_timestamp(d.updated_at)
            datasets.append(dataset)

        return JsonResponse({
            'status': 'success',
            'datasets': datasets,
        })

    @swagger_auto_schema(
        manual_parameters=[AutoSchemaHelper.query_org_id_field()],
        request_body=AutoSchemaHelper.schema_factory(
            {'dataset': 'string'},
            description='The new name for this dataset'
        )
    )
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('can_modify_data')
    def update(self, request, pk=None):
        """
            Updates the name of a dataset (ImportRecord).
        """

        organization_id = self.get_organization(request)
        if organization_id is None:
            return JsonResponse(
                {'status': 'error', 'message': 'Missing organization_id query parameter'})
        try:
            organization_id = int(organization_id)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Bad (non-numeric) organization_id'})
        dataset_id = pk
        name = request.data['dataset']

        # check if user has access to the dataset
        d = ImportRecord.objects.filter(
            super_organization_id=organization_id, pk=dataset_id
        )

        if not d.exists():
            return JsonResponse({
                'status': 'error',
                'message': 'user does not have permission to update dataset',
            }, status=status.HTTP_400_BAD_REQUEST)
        d = d[0]
        d.name = name
        d.save()
        return JsonResponse({
            'status': 'success',
        })

    @swagger_auto_schema_org_query_param
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('can_view_data')
    def retrieve(self, request, pk=None):
        """
            Retrieves a dataset (ImportRecord).
        """

        organization_id = self.get_organization(request)
        if organization_id is None:
            return JsonResponse(
                {'status': 'error', 'message': 'Missing organization_id query parameter'},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            organization_id = int(organization_id)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Bad (non-numeric) organization_id'},
                                status=status.HTTP_400_BAD_REQUEST)

        valid_orgs = OrganizationUser.objects.filter(
            user_id=request.user.id
        ).values_list('organization_id', flat=True).order_by('organization_id')
        if organization_id not in valid_orgs:
            return JsonResponse({
                'status': 'error',
                'message': 'Cannot access datasets for this organization id',
            }, status=status.HTTP_403_FORBIDDEN)

        # check if dataset exists
        try:
            d = ImportRecord.objects.get(pk=pk)
        except ImportRecord.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'dataset with id {} does not exist'.format(pk)
            }, status=status.HTTP_404_NOT_FOUND)

        if d.super_organization_id != organization_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Organization ID mismatch between dataset and organization'
            }, status=status.HTTP_400_BAD_REQUEST)

        dataset = obj_to_dict(d)
        importfiles = []
        for f in d.files:
            importfile = obj_to_dict(f)
            if not f.uploaded_filename:
                importfile['name'] = f.filename_only
            else:
                importfile['name'] = f.uploaded_filename
            importfiles.append(importfile)

        dataset['importfiles'] = importfiles
        if d.last_modified_by:
            dataset['last_modified_by'] = d.last_modified_by.email
        dataset['updated_at'] = convert_to_js_timestamp(d.updated_at)

        return JsonResponse({
            'status': 'success',
            'dataset': dataset,
        })

    @swagger_auto_schema_org_query_param
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_member')
    def destroy(self, request, pk=None):
        """
            Deletes a dataset (ImportRecord).
        """
        organization_id = int(self.get_organization(request))
        dataset_id = pk
        # check if user has access to the dataset
        d = ImportRecord.objects.filter(
            super_organization_id=organization_id, pk=dataset_id
        )
        if not d.exists():
            return JsonResponse({
                'status': 'error',
                'message': 'user does not have permission to deactivate dataset',
            }, status=status.HTTP_403_FORBIDDEN)
        d = d[0]
        d.delete()
        return JsonResponse({'status': 'success'})

    @swagger_auto_schema(
        manual_parameters=[AutoSchemaHelper.query_org_id_field()],
        request_body=AutoSchemaHelper.schema_factory(
            {'name': 'string'},
            description='Name of the dataset to be created'
        ),
        responses={
            200: AutoSchemaHelper.schema_factory({
                'id': 'integer',
                'name': 'string',
            })
        }
    )
    @require_organization_id_class
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('can_modify_data')
    def create(self, request):
        """
        Creates a new empty dataset (ImportRecord).
        """

        body = request.data
        org_id = int(self.get_organization(request))

        try:
            org = Organization.objects.get(pk=org_id)
        except Organization.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'organization_id not provided'},
                                status=status.HTTP_400_BAD_REQUEST)
        record = ImportRecord.objects.create(
            name=body['name'],
            app='seed',
            start_time=timezone.now(),
            created_at=timezone.now(),
            last_modified_by=request.user,
            super_organization=org,
            owner=request.user
        )

        return JsonResponse({'status': 'success', 'id': record.pk, 'name': record.name})

    @swagger_auto_schema(
        manual_parameters=[AutoSchemaHelper.query_org_id_field()],
        responses={
            200: AutoSchemaHelper.schema_factory({
                'datasets_count': 'integer',
            })
        }
    )
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_viewer')
    @require_organization_id_class
    @action(detail=False, methods=['GET'])
    def count(self, request):
        """
        Retrieves the number of datasets for an org.
        """
        org_id = int(self.get_organization(request))

        datasets_count = ImportRecord.objects.filter(super_organization_id=org_id).count()
        return JsonResponse({'status': 'success', 'datasets_count': datasets_count})
