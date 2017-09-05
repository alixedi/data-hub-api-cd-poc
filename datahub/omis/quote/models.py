import uuid
from pathlib import PurePath

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.timezone import now

from datahub.core.models import BaseModel

from datahub.omis.core.utils import generate_reference


QUOTE_TEMPLATE = PurePath(__file__).parent / 'templates/content.md'


class Quote(BaseModel):
    """Details of a quote."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    reference = models.CharField(max_length=100)
    content = models.TextField()

    cancelled_on = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @classmethod
    def generate_reference(cls, order):
        """
        :returns: a random unused reference of form:
                <order.reference>/Q-<(2) lettes>/<(1) number> e.g. GEA962/16/Q-AB1
        :raises RuntimeError: if no reference can be generated.
        """
        def gen():
            return '{letters}{numbers}'.format(
                letters=get_random_string(length=2, allowed_chars='ACEFHJKMNPRTUVWXY'),
                numbers=get_random_string(length=1, allowed_chars='123456789')
            )
        return generate_reference(model=cls, gen=gen, prefix=f'{order.reference}/Q-')

    @classmethod
    def generate_content(cls, order):
        """
        :returns: the quote populated with the given order details.
        """
        return render_to_string(
            QUOTE_TEMPLATE,
            {'order': order}
        )

    def cancel(self, by):
        """Cancel the current quote."""
        if self.is_cancelled():  # already cancelled, skip
            return

        self.cancelled_on = now()
        self.cancelled_by = by
        self.save()

    def is_cancelled(self):
        """
        :returns: True if this quote is cancelled, False otherwise.
        """
        return self.cancelled_on

    def __str__(self):
        """Human-readable representation"""
        return self.reference
