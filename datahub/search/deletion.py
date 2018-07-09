from collections import defaultdict
from contextlib import contextmanager

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_delete, pre_delete

from datahub.core.exceptions import DataHubException
from .apps import get_search_app_by_model, get_search_apps
from .elasticsearch import bulk
from .signals import SignalReceiver


BULK_DELETION_TIMEOUT_SECS = 300
BULK_CHUNK_SIZE = 10000


def delete_documents(index, es_docs):
    """
    Deletes `es_docs` from `index`.

    :raises DataHubException: in case of non 404 errors
    """
    delete_actions = (
        _create_delete_action(index, es_doc['_type'], es_doc['_id'])
        for es_doc in es_docs
    )

    _, errors = bulk(
        actions=delete_actions,
        chunk_size=BULK_CHUNK_SIZE,
        request_timeout=BULK_DELETION_TIMEOUT_SECS,
        raise_on_error=False,
    )

    non_404_errors = [error for error in errors if error['delete']['status'] != 404]
    if non_404_errors:
        raise DataHubException(
            f'One or more errors during an Elasticsearch bulk deletion operation: '
            f'{non_404_errors!r}'
        )


def _create_delete_action(_index, _type, _id):
    return {
        '_op_type': 'delete',
        '_index': _index,
        '_type': _type,
        '_id': _id,
    }


class Collector:
    """
    Collects all the deleted django objects so that they can be deleted from ES.

    Most of the time you will want to use the context manager/decorator
    `update_es_after_deletions` instead.

    Usage:

        collector = Collector()
        collector.connect()  # starts listening to post_delete signals

        # delete django objects

        collector.disconnect()  # stops listening to post_delete signals

        collector.delete_from_es()  # deletes the collected objects from ES

    WARNING: this temporarily disable existing post_delete and pre_delete signal
    receivers defined in all the SearchApps to avoid side effects.
    Also, be careful when starting a transaction (e.g. with `transaction.atomic()`) and
    catching any exception in it. ES deletions would still happen because the
    collector would not be aware of any caught error.
    """

    def __init__(self):
        """Initialises the object."""
        self.signal_receivers_to_add = []
        self.signal_receivers_to_disable = []
        self.deletions = defaultdict(list)

        for search_app in get_search_apps():
            model = search_app.queryset.model

            # set up the receivers to add when collecting the deleted objects
            self.signal_receivers_to_add.append(
                SignalReceiver(post_delete, model, self._collect)
            )

            # get the existing post/pre_delete receivers that need to be
            # disabled in the meantime
            for receiver in search_app.get_signals_receivers():
                if receiver.signal in (post_delete, pre_delete):
                    self.signal_receivers_to_disable.append(receiver)

    def connect(self):
        """Starts listening to post_delete signals on all search models."""
        for receiver in self.signal_receivers_to_add:
            receiver.connect()

        for receiver in self.signal_receivers_to_disable:
            receiver.disconnect()

    def disconnect(self):
        """Starts listening to post_delete signals on all search models."""
        for receiver in self.signal_receivers_to_add:
            receiver.disconnect()

        for receiver in self.signal_receivers_to_disable:
            receiver.connect()

    def _collect(self, sender, instance, **kwargs):
        """Logic that gets run on post_delete."""
        model = instance.__class__
        es_model = get_search_app_by_model(model).es_model

        es_doc = es_model.es_document(instance)
        self.deletions[model].append(es_doc)

    def _delete_from_es(self):
        for model, es_docs in self.deletions.items():
            delete_documents(settings.ES_INDEX, es_docs)

    def delete_from_es(self):
        """Deletes all the deleted django models from ES."""
        transaction.on_commit(self._delete_from_es)


@contextmanager
def update_es_after_deletions():
    """
    Returns a context manager that can be used to automatically delete from ES
    all the django objects deleted in the block.
    It can be used as a decorator as well.

    This works by listening to the `post_delete` django signal, collecting all the deleted
    django objects and deleting all of them from ES in bulk when exiting from the context manager.

    WARNING: this temporarily disable existing post_delete and pre_delete signal
    receivers defined in all the SearchApps to avoid side effects.
    Also, be careful when starting a transaction (e.g. with `transaction.atomic()`) and
    catching any exception in it. ES deletions would still happen because the
    context manager would not be aware of any caught error.
    """
    collector = Collector()
    collector.connect()

    try:
        yield collector
    finally:
        collector.disconnect()

    collector.delete_from_es()