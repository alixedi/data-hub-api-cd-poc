from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.http.multipartparser import parse_header
from oauth2_provider.contrib.rest_framework.permissions import IsAuthenticatedOrTokenHasScope
from rest_framework import HTTP_HEADER_ENCODING, status
from rest_framework.views import APIView

from datahub.core.api_client import APIClient, HawkAuth
from datahub.oauth.scopes import Scope


class ActivityFeedView(APIView):
    """
    Activity Feed View.

    At the moment it just authenticates the user using the default authentication
    for the internal_front_end and acts as a proxy for reading from Activity Stream.

    If the authenticated user doesn't have permissions on all activity models,
    it returns an empty list.
    """

    required_scopes = (Scope.internal_front_end,)
    permission_classes = (IsAuthenticatedOrTokenHasScope,)

    ACTIVITY_MODELS_PERMISSIONS_REQUIRED = (
        'interaction.view_all_interaction',
        'investment.view_all_investmentproject',
        'order.view_order',
    )

    def get(self, request):
        """Proxy for GET requests."""
        content_type = request.content_type or ''

        # check that the content type of the request is json
        base_media_type, _ = parse_header(content_type.encode(HTTP_HEADER_ENCODING))
        if base_media_type != 'application/json':
            return HttpResponse(
                'Please set Content-Type header value to application/json',
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        # if the user doesn't have permissions on all activity models, return an empty list
        # TODO: instead of returning an empty list, we need to filter out the
        # activities that the user doesn't have access to
        if not request.user.has_perms(self.ACTIVITY_MODELS_PERMISSIONS_REQUIRED):
            return JsonResponse(
                {
                    'hits': {
                        'total': 0,
                        'hits': [],
                    },
                },
                status=status.HTTP_200_OK,
                content_type=content_type,
            )

        upstream_response = self._get_upstream_response(request)
        return HttpResponse(
            upstream_response.text,
            status=upstream_response.status_code,
            content_type=upstream_response.headers.get('content-type'),
        )

    def _get_upstream_response(self, request):
        hawk_auth = HawkAuth(
            settings.ACTIVITY_STREAM_OUTGOING_ACCESS_KEY_ID,
            settings.ACTIVITY_STREAM_OUTGOING_SECRET_ACCESS_KEY,
            verify_response=False,
        )

        api_client = APIClient(
            settings.ACTIVITY_STREAM_OUTGOING_URL,
            hawk_auth,
            raise_for_status=False,
        )
        return api_client.request(
            request.method,
            '',
            data=request.body,
            headers={
                'Content-Type': request.content_type,
            },
        )
