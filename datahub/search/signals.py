from django.db.models.signals import post_save
from django.dispatch import receiver

from datahub.company.models import Company as DBCompany, Contact as DBContact
from datahub.core.utils import executor
from datahub.investment.models import InvestmentProject as DBInvestmentProject
from datahub.search import elasticsearch
from datahub.search import models as search_models


def sync_es(search_model, db_model, pk):
    """Sync to ES by instance pk and type."""
    instance = db_model.objects.get(pk=pk)
    doc = search_model.es_document(instance)
    elasticsearch.bulk(actions=(doc, ), chunk_size=1)


@receiver(post_save, sender=DBCompany, dispatch_uid='company_sync_es')
def company_sync_es(sender, instance, **kwargs):
    """Sync company to the Elasticsearch."""
    executor.submit(sync_es, search_models.Company, DBCompany, str(instance.pk))


@receiver(post_save, sender=DBContact, dispatch_uid='contact_sync_es')
def contact_sync_es(sender, instance, **kwargs):
    """Sync contact to the Elasticsearch."""
    executor.submit(sync_es, search_models.Contact, DBContact, str(instance.pk))


@receiver(post_save, sender=DBInvestmentProject, dispatch_uid='investment_project_sync_es')
def investment_project_sync_es(sender, instance, **kwargs):
    """Sync investment project to the Elasticsearch."""
    executor.submit(
        sync_es,
        search_models.InvestmentProject,
        DBInvestmentProject,
        str(instance.pk),
    )
