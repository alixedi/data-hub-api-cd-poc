import datetime

import pytest
from django.utils.timezone import utc
from freezegun import freeze_time

from datahub.company.constants import BusinessTypeConstant
from datahub.company.test.factories import CompanyFactory
from datahub.core.constants import Country, Sector, UKRegion
from datahub.dnb_api.constants import (
    FEATURE_FLAG_DNB_COMPANY_UPDATES,
)
from datahub.feature_flag.test.factories import FeatureFlagFactory
from datahub.interaction.test.factories import CompanyInteractionFactory


@pytest.fixture()
def dnb_company_updates_feature_flag():
    """
    Creates the DNB company updates feature flag.
    """
    yield FeatureFlagFactory(code=FEATURE_FLAG_DNB_COMPANY_UPDATES)


@pytest.fixture
def dnb_response_non_uk():
    """
    Fixture for a record as returned by the dnb-service.
    """
    return {
        'results': [
            {
                'duns_number': '123456789',
                'primary_name': 'Acme Corporation',
                'trading_names': [
                    'Acme',
                ],
                'registration_numbers': [
                    {
                        'registration_type': 'unmapped',
                        'original_registration_type': 6863,
                        'original_registration_number': '24-3733147',
                        'original_registration_description':
                            'Federal Taxpayer Identification Number (US)',
                    },
                ],
                'global_ultimate_duns_number': '157270606',
                'global_ultimate_primary_name': 'Acme Corporation',
                'domain': 'acme.com',
                'is_out_of_business': False,
                'address_line_1': '150 Madison Ave',
                'address_line_2': '',
                'address_town': 'New York',
                'address_county': '',
                'address_postcode': '10033-1062',
                'address_country': 'US',
                'annual_sales': 1000000.0,
                'annual_sales_currency': 'USD',
                'is_annual_sales_estimated': None,
                'employee_number': 100,
                'is_employees_number_estimated': False,
                'primary_industry_codes': [
                    {
                        'usSicV4': '2325',
                        'usSicV4Description': "Mfg men's/boy's trousers",
                    },
                ],
                'industry_codes': [
                    {
                        'code': '315220',
                        'description': 'Men’s and Boys’ Cut and Sew Apparel Manufacturing',
                        'typeDescription': 'North American Industry Classification System 2017',
                        'typeDnbCode': 30832,
                        'priority': 2,
                    },
                    {
                        'code': '315990',
                        'description': 'Apparel Accessories and Other Apparel Manufacturing',
                        'typeDescription': 'North American Industry Classification System 2017',
                        'typeDnbCode': 30832,
                        'priority': 4,
                    },
                ],
                'legal_status': 'corporation',
            },
        ],
    }


@pytest.fixture
def dnb_company_updates_response_uk(dnb_response_uk):
    """
    Returns a UK based DNB company in the format of the "company update" API endpoint
    for dnb-service.
    """
    return {
        **dnb_response_uk,
        'next': None,
    }


@pytest.fixture
def dnb_company_search_datahub_companies():
    """
    Creates Data Hub companies for hydrating DNB search results with.
    """
    # Company with no interactions
    CompanyFactory(duns_number='1234567', id='6083b732-b07a-42d6-ada4-c8082293285b')
    # Company with two interactions
    company = CompanyFactory(duns_number='7654321', id='6083b732-b07a-42d6-ada4-c99999999999')

    interaction_date = datetime.datetime(year=2019, month=8, day=1, hour=16, minute=0, tzinfo=utc)
    with freeze_time(interaction_date):
        CompanyInteractionFactory(
            id='6083b732-b07a-42d6-ada4-222222222222',
            date=interaction_date,
            subject='Meeting with Joe Bloggs',
            company=company,
        )

    older_interaction_date = datetime.datetime(year=2018, month=8, day=1, tzinfo=utc)
    with freeze_time(older_interaction_date):
        CompanyInteractionFactory(
            id='6083b732-b07a-42d6-ada4-111111111111',
            date=older_interaction_date,
            subject='Meeting with John Smith',
            company=company,
        )


@pytest.fixture
def investigation_payload():
    """
    Valid DNB company investigation payload.
    """
    return {
        'business_type': BusinessTypeConstant.company.value.id,
        'name': 'Test Company',
        'website': 'http://www.test.com',
        'telephone_number': '12345678',
        'address': {
            'line_1': 'Foo',
            'line_2': 'Bar',
            'town': 'Baz',
            'county': 'Qux',
            'country': {
                'id': Country.united_kingdom.value.id,
            },
            'postcode': 'AB5 XY2',
        },
        'sector': Sector.renewable_energy_wind.value.id,
        'uk_region': UKRegion.east_midlands.value.id,
    }
