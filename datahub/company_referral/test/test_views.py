from collections.abc import Mapping
from datetime import datetime
from unittest.mock import ANY
from uuid import UUID

import pytest
from django.utils.timezone import utc
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse

from datahub.company.test.factories import AdviserFactory, CompanyFactory, ContactFactory
from datahub.company_referral.models import CompanyReferral
from datahub.core.test_utils import APITestMixin, create_test_user, format_date_or_datetime

FROZEN_DATETIME = datetime(2020, 1, 24, 16, 26, 50, tzinfo=utc)

collection_url = reverse('api-v4:company-referral:collection')


class TestAddCompanyReferral(APITestMixin):
    """Tests for the add company referral view."""

    def test_returns_401_if_unauthenticated(self, api_client):
        """Test that a 401 is returned if the user is unauthenticated."""
        response = api_client.post(collection_url, data={})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        'permission_codenames,expected_status',
        (
            ([], status.HTTP_403_FORBIDDEN),
            (['add_companyreferral'], status.HTTP_201_CREATED),
        ),
    )
    def test_permission_checking(self, permission_codenames, expected_status, api_client):
        """
        Test that the expected status is returned depending on the permissions the user has.
        """
        user = create_test_user(permission_codenames=permission_codenames)
        api_client = self.create_api_client(user=user)

        request_data = {
            'subject': 'Test referral',
            'company': {
                'id': CompanyFactory().pk,
            },
            'recipient': {
                'id': AdviserFactory().pk,
            },
        }

        response = api_client.post(collection_url, data=request_data)
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        'request_data,expected_response_data',
        (
            pytest.param(
                {},
                {
                    'company': ['This field is required.'],
                    'recipient': ['This field is required.'],
                    'subject': ['This field is required.'],
                },
                id='omitted-fields',
            ),
            pytest.param(
                {
                    'company': None,
                    'notes': None,
                    'recipient': None,
                    'subject': None,
                },
                {
                    'company': ['This field may not be null.'],
                    'notes': ['This field may not be null.'],
                    'recipient': ['This field may not be null.'],
                    'subject': ['This field may not be null.'],
                },
                id='non-null-fields',
            ),
            pytest.param(
                {
                    # The value this field shouldn't be allowed to be an empty string
                    'subject': '',

                    # Provide values for other required fields (so we don't get errors for them)
                    'company': {
                        'id': CompanyFactory,
                    },
                    'recipient': {
                        'id': AdviserFactory,
                    },
                },
                {
                    'subject': ['This field may not be blank.'],
                },
                id='non-blank-fields',
            ),
        ),
    )
    def test_validates_input(self, request_data, expected_response_data):
        """Test validation for various scenarios."""
        resolved_request_data = _resolve_data(request_data)
        response = self.api_client.post(collection_url, data=resolved_request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected_response_data

    @freeze_time(FROZEN_DATETIME)
    def test_can_create_a_referral_without_optional_fields(self):
        """Test that a referral can be created without optional values filled in."""
        company = CompanyFactory()
        recipient = AdviserFactory()
        subject = 'Test referral'

        request_data = {
            'subject': subject,
            'company': {
                'id': company.pk,
            },
            'recipient': {
                'id': recipient.pk,
            },
        }

        response = self.api_client.post(collection_url, data=request_data)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data == {
            'company': {
                'id': str(company.pk),
                'name': company.name,
            },
            'completed_on': None,
            'contact': None,
            'created_by': {
                'contact_email': self.user.contact_email,
                'dit_team': {
                    'id': str(self.user.dit_team.pk),
                    'name': self.user.dit_team.name,
                },
                'id': str(self.user.pk),
                'name': self.user.name,
            },
            'created_on': format_date_or_datetime(FROZEN_DATETIME),
            'id': ANY,
            'notes': '',
            'recipient': {
                'contact_email': recipient.contact_email,
                'dit_team': {
                    'id': str(recipient.dit_team.pk),
                    'name': recipient.dit_team.name,
                },
                'id': str(recipient.pk),
                'name': recipient.name,
            },
            'status': CompanyReferral.STATUSES.outstanding,
            'subject': subject,
        }

    @freeze_time(FROZEN_DATETIME)
    def test_can_create_a_referral_with_optional_fields(self):
        """Test that a referral can be created with all optional values filled in."""
        company = CompanyFactory()
        contact = ContactFactory()
        recipient = AdviserFactory()
        subject = 'Test referral'
        notes = 'Some notes'

        request_data = {
            'subject': subject,
            'company': {
                'id': company.pk,
            },
            'recipient': {
                'id': recipient.pk,
            },
            'contact': {
                'id': contact.pk,
            },
            'notes': notes,
        }

        response = self.api_client.post(collection_url, data=request_data)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data == {
            'company': {
                'id': str(company.pk),
                'name': company.name,
            },
            'completed_on': None,
            'contact': {
                'id': str(contact.pk),
                'name': contact.name,
            },
            'created_by': {
                'contact_email': self.user.contact_email,
                'dit_team': {
                    'id': str(self.user.dit_team.pk),
                    'name': self.user.dit_team.name,
                },
                'id': str(self.user.pk),
                'name': self.user.name,
            },
            'created_on': format_date_or_datetime(FROZEN_DATETIME),
            'id': ANY,
            'notes': notes,
            'recipient': {
                'contact_email': recipient.contact_email,
                'dit_team': {
                    'id': str(recipient.dit_team.pk),
                    'name': recipient.dit_team.name,
                },
                'id': str(recipient.pk),
                'name': recipient.name,
            },
            'status': CompanyReferral.STATUSES.outstanding,
            'subject': subject,
        }

    @freeze_time(FROZEN_DATETIME)
    def test_persists_data_to_the_database(self):
        """Test that created referrals are saved to the database."""
        request_data = {
            'subject': 'Test referral',
            'company': {
                'id': CompanyFactory().pk,
            },
            'contact': {
                'id': ContactFactory().pk,
            },
            'notes': 'Test notes',
            'recipient': {
                'id': AdviserFactory().pk,
            },
        }

        response = self.api_client.post(collection_url, data=request_data)
        assert response.status_code == status.HTTP_201_CREATED

        pk = response.json()['id']
        referral_data = CompanyReferral.objects.values().get(pk=pk)

        assert referral_data == {
            'company_id': request_data['company']['id'],
            'completed_by_id': None,
            'completed_on': None,
            'contact_id': request_data['contact']['id'],
            'created_by_id': self.user.pk,
            'created_on': FROZEN_DATETIME,
            'id': UUID(pk),
            'modified_by_id': self.user.pk,
            'modified_on': FROZEN_DATETIME,
            'notes': request_data['notes'],
            'recipient_id': request_data['recipient']['id'],
            'status': CompanyReferral.STATUSES.outstanding,
            'subject': request_data['subject'],
        }


def _resolve_data(data):
    """Resolve callables in values used in parametrised tests."""
    if isinstance(data, Mapping):
        return {key: _resolve_data(value) for key, value in data.items()}

    if callable(data):
        resolved_value = data()
    else:
        resolved_value = data

    return getattr(resolved_value, 'pk', resolved_value)
