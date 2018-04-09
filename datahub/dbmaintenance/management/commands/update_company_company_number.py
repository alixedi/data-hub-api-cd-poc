from logging import getLogger

import reversion

from datahub.company.models import Company
from datahub.dbmaintenance.utils import parse_limited_string, parse_uuid
from ..base import CSVBaseCommand


logger = getLogger(__name__)


class Command(CSVBaseCommand):
    """Command to update Company.company_number."""

    def add_arguments(self, parser):
        """Define extra arguments."""
        super().add_arguments(parser)
        parser.add_argument(
            '--simulate',
            action='store_true',
            default=False,
            help='If True it only simulates the command without saving changes.',
        )

    def _process_row(self, row, simulate=False, **options):
        """Process one single row."""
        pk = parse_uuid(row['id'])
        company = Company.objects.get(pk=pk)
        company_number = parse_limited_string(row['company_number'])

        if company.company_number == company_number:
            return

        company.company_number = company_number

        if simulate:
            return

        with reversion.create_revision():
            company.save(update_fields=('company_number',))
            reversion.set_comment('Company number updated.')