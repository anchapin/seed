# !/usr/bin/env python
# encoding: utf-8

from drf_yasg.utils import swagger_auto_schema

from rest_framework import viewsets
from rest_framework.decorators import action

from seed.decorators import ajax_request_class
from seed.lib.superperms.orgs.decorators import has_perm_class
from seed.models.properties import PropertyState
from seed.models.tax_lots import TaxLotState
from seed.utils.api import api_endpoint_class
from seed.utils.api_schema import AutoSchemaHelper
from seed.utils.ubid import decode_unique_ids


class UbidViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        manual_parameters=[AutoSchemaHelper.query_org_id_field()],
        request_body=AutoSchemaHelper.schema_factory(
            {
                'property_view_ids': ['integer'],
                'taxlot_view_ids': ['integer'],
            },
            description='IDs by inventory type for records to have their UBID decoded.'
        )
    )
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('can_modify_data')
    @action(detail=False, methods=['POST'])
    def decode_by_ids(self, request):
        body = dict(request.data)
        property_view_ids = body.get('property_view_ids')
        taxlot_view_ids = body.get('taxlot_view_ids')

        if property_view_ids:
            property_views = PropertyView.objects.filter(id__in=property_view_ids)
            properties = PropertyState.objects.filter(
                id__in=Subquery(property_views.values('state_id'))
            )
            decode_unique_ids(properties)

        if taxlot_view_ids:
            taxlot_views = TaxLotView.objects.filter(id__in=taxlot_view_ids)
            taxlots = TaxLotState.objects.filter(
                id__in=Subquery(taxlot_views.values('state_id'))
            )
            decode_unique_ids(taxlots)

        return JsonResponse({'status': 'success'})

    @ajax_request_class
    @action(detail=False, methods=['POST'])
    def decode_results(self, request):
        body = dict(request.data)

        ubid_unpopulated = 0
        ubid_successfully_decoded = 0
        ubid_not_decoded = 0
        ulid_unpopulated = 0
        ulid_successfully_decoded = 0
        ulid_not_decoded = 0
        property_ids = body.get('property_ids')
        taxlot_ids = body.get('taxlot_ids')
        if property_ids:
            properties = PropertyState.objects.filter(id__in=property_ids)
            ubid_unpopulated = len(properties.filter(ubid__isnull=True))
            ubid_successfully_decoded = len(properties.filter(ubid__isnull=False,
                                                              bounding_box__isnull=False,
                                                              centroid__isnull=False))
            # for ubid_not_decoded, bounding_box could be populated from a GeoJSON import
            ubid_not_decoded = len(properties.filter(ubid__isnull=False, centroid__isnull=True))

        if taxlot_ids:
            taxlots = TaxLotState.objects.filter(id__in=taxlot_ids)
            ulid_unpopulated = len(taxlots.filter(ulid__isnull=True))
            ulid_successfully_decoded = len(taxlots.filter(ulid__isnull=False,
                                                           bounding_box__isnull=False,
                                                           centroid__isnull=False))
            # for ulid_not_decoded, bounding_box could be populated from a GeoJSON import
            ulid_not_decoded = len(taxlots.filter(ulid__isnull=False, centroid__isnull=True))

        result = {
            "ubid_unpopulated": ubid_unpopulated,
            "ubid_successfully_decoded": ubid_successfully_decoded,
            "ubid_not_decoded": ubid_not_decoded,
            "ulid_unpopulated": ulid_unpopulated,
            "ulid_successfully_decoded": ulid_successfully_decoded,
            "ulid_not_decoded": ulid_not_decoded,
        }

        return result
