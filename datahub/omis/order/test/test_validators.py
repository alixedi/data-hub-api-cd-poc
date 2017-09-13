from unittest import mock
import pytest

from rest_framework.exceptions import ValidationError

from datahub.omis.core.exceptions import Conflict

from .factories import (
    OrderFactory,
    OrderWithCancelledQuoteFactory,
    OrderWithOpenQuoteFactory,
)

from ..constants import OrderStatus, VATStatus
from ..models import Order
from ..validators import (
    ContactWorksAtCompanyValidator,
    NoOtherActiveQuoteExistsValidator,
    OrderDetailsFilledInValidator,
    OrderInStatusValidator,
    ReadonlyAfterCreationValidator,
    VATValidator,
)


class TestContactWorksAtCompanyValidator:
    """Tests for ContactWorksAtCompanyValidator."""

    def test_contact_from_company(self):
        """
        Test that if the contact specified in data works
        at the company specified in data, the validation passes.
        """
        serializer = mock.Mock()
        company = serializer.instance.company
        new_contact = mock.Mock(company=company)

        validator = ContactWorksAtCompanyValidator()
        validator.set_context(serializer)

        try:
            validator({
                'contact': new_contact,
                'company': company
            })
        except Exception:
            pytest.fail('Should not raise a validator error.')

    def test_contact_not_from_company(self):
        """
        Test that if the contact specified in data doesn't works
        at the company specified in data, the validation fails.
        """
        serializer = mock.Mock()
        company = serializer.instance.company
        new_contact = mock.Mock()  # doesn't work at `company`

        validator = ContactWorksAtCompanyValidator()
        validator.set_context(serializer)

        with pytest.raises(ValidationError):
            validator({
                'contact': new_contact,
                'company': company
            })

    def test_with_different_field_names(self):
        """
        Test that the validation passes when using different field names.
        """
        serializer = mock.Mock()
        company = serializer.instance.company
        new_main_contact = mock.Mock(company=company)

        validator = ContactWorksAtCompanyValidator(
            contact_field='main_contact',
            company_field='main_company'
        )
        validator.set_context(serializer)

        try:
            validator({
                'main_contact': new_main_contact,
                'main_company': company
            })
        except Exception:
            pytest.fail('Should not raise a validator error.')


class TestReadonlyAfterCreationValidator:
    """Tests for ReadonlyAfterCreationValidator."""

    def test_can_change_when_creating(self):
        """Test that if we are creating the instance, the validation passes."""
        serializer = mock.Mock(instance=None)

        validator = ReadonlyAfterCreationValidator(
            fields=('field1', 'field2')
        )
        validator.set_context(serializer)

        try:
            validator({
                'field1': 'some value',
                'field2': 'some value',
            })
        except Exception:
            pytest.fail('Should not raise a validator error.')

    def test_cannot_change_after_creation(self):
        """
        Test that if we are updating the instance and we try to update the fields,
        the validation fails.
        """
        serializer = mock.Mock()  # serializer.instance is != None

        validator = ReadonlyAfterCreationValidator(
            fields=('field1', 'field2')
        )
        validator.set_context(serializer)

        with pytest.raises(ValidationError):
            validator({
                'field1': 'some value',
                'field2': 'some value',
            })

    def test_ok_if_the_values_dont_change_after_creation(self):
        """
        Test that if we are updating the instance and we don't update the fields,
        the validation passes.
        """
        serializer = mock.Mock()
        instance = serializer.instance

        validator = ReadonlyAfterCreationValidator(
            fields=('field1', 'field2')
        )
        validator.set_context(serializer)

        try:
            validator({
                'field1': instance.field1,
                'field2': instance.field2,
            })
        except Exception:
            pytest.fail('Should not raise a validator error.')


@pytest.mark.django_db
class TestOrderDetailsFilledInValidator:
    """Tests for the OrderDetailsFilledInValidator."""

    @pytest.mark.parametrize('values_as_data', (True, False))
    def test_incomplete_order(self, values_as_data):
        """
        Test that an incomplete order doesn't pass the validation.

        Test both scenarios:
        - with fields on the instance (values_as_data=False)
        - with fields as values in the data param (values_as_data=True)
        """
        order_fields = {
            'primary_market': None,
            'service_types': [],
            'description': '',
            'delivery_date': None,
            'vat_status': '',
        }
        order = Order(**(order_fields if not values_as_data else {}))
        data = order_fields if values_as_data else {}

        validator = OrderDetailsFilledInValidator()
        validator.set_instance(order)

        with pytest.raises(ValidationError) as exc:
            validator(data)

        assert exc.value.detail == {
            field: ['This field is required.'] for field in order_fields
        }

    @pytest.mark.parametrize('values_as_data', (True, False))
    def test_complete_order(self, values_as_data):
        """
        Test that a complete order passes the validation.

        Test both scenarios:
        - with fields on the instance (values_as_data=False)
        - with fields as values in the data param (values_as_data=True)
        """
        random_values = OrderFactory()  # used only to set up the related props easily

        order_fields = {
            'primary_market': random_values.primary_market,
            'service_types': random_values.service_types.all(),
            'description': random_values.description,
            'delivery_date': random_values.delivery_date,
            'vat_status': random_values.vat_status,
        }
        order = OrderFactory(**(order_fields if not values_as_data else {}))
        data = order_fields if values_as_data else {}

        validator = OrderDetailsFilledInValidator()
        validator.set_instance(order)

        try:
            validator(data)
        except Exception:
            pytest.fail('Should not raise a validator error.')

    def test_validation_errors_appended(self):
        """
        Test that if a field gets more than one error during the validation,
        the errors are appended to the same list and not overridden by other validators.
        """
        order = OrderFactory()

        with mock.patch.object(
            OrderDetailsFilledInValidator,
            'get_extra_validators'
        ) as get_extra_validators:

            # trigger a second validation error on the same field
            get_extra_validators.return_value = [
                mock.Mock(
                    side_effect=ValidationError({
                        'description': ['A different error...']
                    })
                )
            ]

            validator = OrderDetailsFilledInValidator()
            validator.set_instance(order)

            with pytest.raises(ValidationError) as exc:
                validator({
                    'description': ''
                })

            assert exc.value.detail == {
                'description': [
                    'This field is required.',
                    'A different error...'
                ]
            }


@pytest.mark.django_db
class TestNoOtherActiveQuoteExistsValidator:
    """Tests for the NoOtherActiveQuoteExistsValidator."""

    def test_with_existing_active_quote(self):
        """Test that if there's already an active quote, the validation fails."""
        order = OrderWithOpenQuoteFactory()

        validator = NoOtherActiveQuoteExistsValidator()
        validator.set_instance(order)

        with pytest.raises(Conflict):
            validator()

    def test_without_any_active_quote(self):
        """Test that if there isn't any active quote, the validation passes."""
        order = OrderFactory()

        validator = NoOtherActiveQuoteExistsValidator()
        validator.set_instance(order)

        try:
            validator()
        except Exception:
            pytest.fail('Should not raise a validator error.')

    def test_with_cancelled_quote(self):
        """Test that if there is a cancelled quote, the validation passes."""
        order = OrderWithCancelledQuoteFactory()

        validator = NoOtherActiveQuoteExistsValidator()
        validator.set_instance(order)

        try:
            validator()
        except Exception:
            pytest.fail('Should not raise a validator error.')


@pytest.mark.django_db
class TestOrderInStatusValidator:
    """Tests for the OrderInStatusValidator."""

    def test_validation_passes(self):
        """
        Test that the validation passes if order.status is one of the allowed statuses.
        """
        order = OrderFactory(status=OrderStatus.complete)

        validator = OrderInStatusValidator(
            allowed_statuses=(
                OrderStatus.draft,
                OrderStatus.complete,
                OrderStatus.cancelled
            )
        )
        validator.set_instance(order)

        try:
            validator()
        except Exception:
            pytest.fail('Should not raise a validator error.')

    def test_validation_fails(self):
        """
        Test that the validation fails if order.status is NOT one of the allowed statuses.
        """
        order = OrderFactory(status=OrderStatus.complete)

        validator = OrderInStatusValidator(
            allowed_statuses=(
                OrderStatus.draft,
                OrderStatus.cancelled
            )
        )
        validator.set_instance(order)

        with pytest.raises(Conflict):
            validator()

    def test_set_instance_via_serializer_instance(self):
        """
        Test that seriaizer.set_context gets the order from serializer.instance.
        """
        order = Order()
        serializer = mock.Mock(instance=order, context={})

        validator = OrderInStatusValidator(allowed_statuses=())
        validator.set_context(serializer)
        assert validator.instance == order

    def test_set_instance_via_serializer_context(self):
        """
        Test that seriaizer.set_context gets the order from serializer.context['order'].
        """
        order = Order()
        serializer = mock.Mock(context={'order': order})

        validator = OrderInStatusValidator(allowed_statuses=())
        validator.set_context(serializer)
        assert validator.instance == order

    def test_order_not_required(self):
        """
        Test that if order_required == False and the order passed in is None,
        the validation passes.
        """
        validator = OrderInStatusValidator(
            allowed_statuses=(
                OrderStatus.draft,
                OrderStatus.complete,
                OrderStatus.cancelled
            ),
            order_required=False
        )
        validator.set_instance(None)

        try:
            validator()
        except Exception:
            pytest.fail('Should not raise a validator error.')


class TestVATValidator:
    """Tests for the VATValidator."""

    @pytest.mark.parametrize('values_as_data', (True, False))
    def test_nothing_specified_fails(self, values_as_data):
        """
        Test that if none of the vat fields are specified, it raises a ValidationError.

        Test both scenarios:
        - with fields on the instance (values_as_data=False)
        - with fields as values in the data param (values_as_data=True)
        """
        order_fields = {
            'vat_status': '',
            'vat_number': '',
            'vat_verified': None
        }

        order = Order(**(order_fields if not values_as_data else {}))
        data = order_fields if values_as_data else {}

        validator = VATValidator()
        validator.set_instance(order)

        with pytest.raises(ValidationError) as exc:
            validator(data)
        assert exc.value.detail == {'vat_status': ['This field is required.']}

    @pytest.mark.parametrize('values_as_data', (True, False))
    def test_only_status_eu_specified_fails(self, values_as_data):
        """
        Test that if only vat_status = eu is specified, it raises a ValidationError
        as vat_verified (true or false) has to be specified as well.

        Test both scenarios:
        - with fields on the instance (values_as_data=False)
        - with fields as values in the data param (values_as_data=True)
        """
        order_fields = {
            'vat_status': VATStatus.eu,
            'vat_number': '',
            'vat_verified': None
        }

        order = Order(**(order_fields if not values_as_data else {}))
        data = order_fields if values_as_data else {}

        validator = VATValidator()
        validator.set_instance(order)

        with pytest.raises(ValidationError) as exc:
            validator(data)
        assert exc.value.detail == {'vat_verified': ['This field is required.']}

    @pytest.mark.parametrize('values_as_data', (True, False))
    def test_only_status_eu_verified_true_specified_fails(self, values_as_data):
        """
        Test that if vat_status = eu and vat_verified = True but vat_number is not specified,
        it raises a ValidationError.

        Test both scenarios:
        - with fields on the instance (values_as_data=False)
        - with fields as values in the data param (values_as_data=True)
        """
        order_fields = {
            'vat_status': VATStatus.eu,
            'vat_number': '',
            'vat_verified': True
        }

        order = Order(**(order_fields if not values_as_data else {}))
        data = order_fields if values_as_data else {}

        validator = VATValidator()
        validator.set_instance(order)

        with pytest.raises(ValidationError) as exc:
            validator(data)
        assert exc.value.detail == {'vat_number': ['This field is required.']}

    @pytest.mark.parametrize('values_as_data', (True, False))
    def test_complete_verified_eu_vat_succeeds(self, values_as_data):
        """
        Test that if vat_status = eu, vat_verified = True and vat_number is specified,
        the validation passes.

        Test both scenarios:
        - with fields on the instance (values_as_data=False)
        - with fields as values in the data param (values_as_data=True)
        """
        order_fields = {
            'vat_status': VATStatus.eu,
            'vat_number': '0123456789',
            'vat_verified': True
        }

        order = Order(**(order_fields if not values_as_data else {}))
        data = order_fields if values_as_data else {}

        validator = VATValidator()
        validator.set_instance(order)

        try:
            validator(data)
        except Exception:
            pytest.fail('Should not raise a validator error.')

    @pytest.mark.parametrize('values_as_data', (True, False))
    def test_only_status_eu_verified_false_specified_succeeds(self, values_as_data):
        """
        Test that if vat_status = eu, vat_verified = False and vat_number is not specified,
        the validation passes and vat_number is not required when vat_verified is False.

        Test both scenarios:
        - with fields on the instance (values_as_data=False)
        - with fields as values in the data param (values_as_data=True)
        """
        order_fields = {
            'vat_status': VATStatus.eu,
            'vat_number': '',
            'vat_verified': False
        }

        order = Order(**(order_fields if not values_as_data else {}))
        data = order_fields if values_as_data else {}

        validator = VATValidator()
        validator.set_instance(order)

        try:
            validator(data)
        except Exception:
            pytest.fail('Should not raise a validator error.')

    @pytest.mark.parametrize('values_as_data', (True, False))
    @pytest.mark.parametrize('vat_status', (VATStatus.outside_eu, VATStatus.uk))
    def test_only_status_non_eu_succeeds(self, values_as_data, vat_status):
        """
        Test that if vat_status != eu, the validation passes even if the other
        fields are empty.

        Test both scenarios:
        - with fields on the instance (values_as_data=False)
        - with fields as values in the data param (values_as_data=True)
        """
        order_fields = {
            'vat_status': vat_status,
            'vat_number': '',
            'vat_verified': None
        }

        order = Order(**(order_fields if not values_as_data else {}))
        data = order_fields if values_as_data else {}

        validator = VATValidator()
        validator.set_instance(order)

        try:
            validator(data)
        except Exception:
            pytest.fail('Should not raise a validator error.')
