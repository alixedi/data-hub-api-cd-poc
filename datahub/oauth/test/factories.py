import factory
from django.utils.timezone import utc
from oauth2_provider.models import AccessToken, Application


class ApplicationFactory(factory.django.DjangoModelFactory):
    """Application factory."""

    name = factory.Faker('words', nb=3)
    client_type = Application.CLIENT_CONFIDENTIAL
    authorization_grant_type = Application.GRANT_CLIENT_CREDENTIALS

    class Meta:
        model = Application


class OAuthApplicationScopeFactory(factory.django.DjangoModelFactory):
    """ApplicationScope factory."""

    application = factory.SubFactory(ApplicationFactory)

    class Meta:
        model = 'oauth.OAuthApplicationScope'


class AccessTokenFactory(factory.django.DjangoModelFactory):
    """AccessToken factory."""

    token = factory.Faker('password', length=20)
    expires = factory.Faker('date_time_between', start_date='+1d', end_date='+7d', tzinfo=utc)

    class Meta:
        model = AccessToken
