import pytest

from datahub.company.test.factories import AdviserFactory
from datahub.dataset.investment_project.pagination import (
    InvestmentProjectActivityDatasetViewCursorPagination,
)

pytestmark = pytest.mark.django_db


def test_cursor_pagination_transforms_spi_record_row():
    """Test that cursor transforms SPI record into expected format."""
    pagination = InvestmentProjectActivityDatasetViewCursorPagination()
    spi_report = [
        {
            'Project created on': 'project_created_on',
            'Enquiry processed': 'enquiry_processed',
            'Enquiry type': 'enquiry_type',
            'Enquiry processed by': str(AdviserFactory().id),
            'Assigned to IST': 'assigned_to_ist',
            'Project manager assigned': 'project_manager_assigned',
            'Project manager assigned by': str(AdviserFactory().id),
            'Propositions': [{
                'deadline': 'deadline',
                'status': 'status',
                'modified_on': 'modified_on',
                'adviser_id': 'adviser_id',
            }],
            'Project moved to won': 'project_moved_to_won',
            'Aftercare offered on': 'aftercare_offered_on',
            'Project ID': 'project_id',
            'Data Hub ID': 'data_hub_id',
            'Project name': 'project_name',
        },
    ]
    response = list(pagination._map_results(spi_report))
    assert response == [{
        'enquiry_processed': 'enquiry_processed',
        'enquiry_type': 'enquiry_type',
        'enquiry_processed_by_id': spi_report[0]['Enquiry processed by'],
        'assigned_to_ist': 'assigned_to_ist',
        'project_manager_assigned': 'project_manager_assigned',
        'project_manager_assigned_by_id': spi_report[0]['Project manager assigned by'],
        'propositions': [{
            'deadline': 'deadline',
            'status': 'status',
            'modified_on': 'modified_on',
            'adviser_id': 'adviser_id',
        }],
        'project_moved_to_won': 'project_moved_to_won',
        'aftercare_offered_on': 'aftercare_offered_on',
        'investment_project_id': 'data_hub_id',
    }]
