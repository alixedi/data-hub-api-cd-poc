"""
Pagination serializers determine the structure of the output that should
be used for paginated responses.
"""
from collections import OrderedDict

from dateutil.parser import parse as dateutil_parse
from rest_framework.response import Response

from datahub.dataset.core.pagination import DatasetCursorPagination
from datahub.investment.project.proposition.models import PropositionStatus
from datahub.investment.project.report.spi import SPIReport


class InvestmentProjectActivityDatasetViewCursorPagination(DatasetCursorPagination):
    """Cursor Pagination for SPI Report."""

    ordering = ('id', )

    required_fields_label_mapping = {
        'Data Hub ID': 'investment_project_id',
        'Enquiry processed': 'enquiry_processed',
        'Enquiry type': 'enquiry_type',
        'Enquiry processed by': 'enquiry_processed_by_id',
        'Assigned to IST': 'assigned_to_ist',
        'Project manager assigned': 'project_manager_assigned',
        'Project manager assigned by': 'project_manager_assigned_by_id',
        'Project moved to won': 'project_moved_to_won',
        'Aftercare offered on': 'aftercare_offered_on',
        'Propositions': 'propositions',
    }

    required_fields_value_mapping = {
        'Enquiry processed by': lambda adviser: str(adviser),
        'Project manager assigned by': lambda adviser: str(adviser.id),
    }

    def __init__(self):
        """Initialise the pagination with SPI report instance."""
        super().__init__()
        self._SPIReport = SPIReport(proposition_formatter=self._proposition_formatter)

    def _proposition_formatter(self, propositions):
        """Returns a list of propositions with selected fields."""
        return [{
            'deadline': dateutil_parse(proposition['deadline']).strftime('%Y-%m-%d'),
            'status': proposition['status'],
            'modified_on': dateutil_parse(proposition['modified_on']).isoformat()
            if proposition['status'] != PropositionStatus.ongoing else '',
            'adviser_id': proposition['adviser_id'],
        } for proposition in propositions]

    def _map_results(self, results):
        """Map results into desired format."""
        for result in results:
            yield {
                self.required_fields_label_mapping[key]: value
                for key, value in result.items()
                if key in self.required_fields_label_mapping
            }

    def _get_data(self, investment_projects):
        """
        Enrich Investment Project record with SPI report data and only include required fields.
        """
        for investment_project in investment_projects:
            yield self._SPIReport.get_row(investment_project)

    def get_paginated_response(self, data):
        """Get paginated response."""
        data = self._get_data(data)
        results = self._map_results(data)
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', results),
        ]))
